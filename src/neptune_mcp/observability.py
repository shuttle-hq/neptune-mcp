import os
import importlib
import time
import functools
import inspect
from typing import Any, Callable, Awaitable

from loguru import logger as log


def _env_truthy(value: str | None) -> bool:
    if value is None:
        return False
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def telemetry_disabled() -> bool:
    # User-controlled kill switch (works everywhere: CLI, MCP clients, services).
    return _env_truthy(os.getenv("NEPTUNE_MCP_DISABLE_TELEMETRY"))


def init_langtrace() -> bool:
    """Initialize Langtrace tracing if LANGTRACE_API_KEY is available."""
    if telemetry_disabled():
        log.debug("Telemetry disabled via NEPTUNE_MCP_DISABLE_TELEMETRY")
        return False

    api_key = os.getenv("LANGTRACE_API_KEY")
    if not api_key:
        log.debug("Langtrace not initialized (LANGTRACE_API_KEY not set)")
        return False

    try:
        # Must precede any llm module imports
        langtrace = importlib.import_module("langtrace_python_sdk").langtrace
        langtrace.init(api_key=api_key)
        log.info("Telemetry enabled (Langtrace)")
        return True
    except Exception as e:
        # Observability should never take the server down.
        log.warning(f"Langtrace init failed: {e}")
        return False


def _get_tracer():
    """Return an OpenTelemetry tracer (no-op if OTEL isn't configured)."""
    try:
        trace = importlib.import_module("opentelemetry.trace")
        return trace.get_tracer("neptune_mcp")
    except Exception:
        return None


def _set_span_error(span: Any, exc: BaseException) -> None:
    """Best-effort marking of an OTEL span as errored without leaking secrets."""
    try:
        span.record_exception(exc)
    except Exception:
        pass
    try:
        status_mod = importlib.import_module("opentelemetry.trace.status")
        span.set_status(status_mod.Status(status_mod.StatusCode.ERROR, type(exc).__name__))
    except Exception:
        try:
            span.set_attribute("error", True)
            span.set_attribute("exception.type", type(exc).__name__)
        except Exception:
            pass


def _safe_arg_summary(kwargs: dict[str, Any]) -> dict[str, Any]:
    """Return a non-sensitive summary of kwargs (no values)."""
    return {
        "arg.count": len(kwargs),
        "arg.names": ",".join(sorted(kwargs.keys()))[:512],
    }


def instrument_tool_fn(tool_name: str, fn: Callable[..., Any]) -> Callable[..., Any]:
    """Wrap a FastMCP tool function with an OTEL span.

    - Does NOT capture argument values (to avoid secrets)
    - Captures duration + success/error
    """
    if telemetry_disabled():
        return fn

    tracer = _get_tracer()
    if tracer is None:
        return fn

    is_async = inspect.iscoroutinefunction(fn)

    if is_async:

        @functools.wraps(fn)
        async def _wrapped(*args: Any, **kwargs: Any) -> Any:
            span = None
            start = time.perf_counter()
            try:
                span_cm = tracer.start_as_current_span(f"mcp.tool:{tool_name}")
                span = span_cm.__enter__()
                span.set_attribute("mcp.tool.name", tool_name)
                for k, v in _safe_arg_summary(kwargs).items():
                    span.set_attribute(f"mcp.{k}", v)
                result = await fn(*args, **kwargs)
                span.set_attribute("mcp.success", True)
                return result
            except Exception as e:
                if span is not None:
                    _set_span_error(span, e)
                raise
            finally:
                duration_ms = (time.perf_counter() - start) * 1000
                try:
                    if span is not None:
                        span.set_attribute("mcp.duration_ms", duration_ms)
                except Exception:
                    pass
                try:
                    if span is not None:
                        span_cm.__exit__(None, None, None)
                except Exception:
                    pass

        return _wrapped

    @functools.wraps(fn)
    def _wrapped(*args: Any, **kwargs: Any) -> Any:
        span = None
        start = time.perf_counter()
        try:
            span_cm = tracer.start_as_current_span(f"mcp.tool:{tool_name}")
            span = span_cm.__enter__()
            span.set_attribute("mcp.tool.name", tool_name)
            for k, v in _safe_arg_summary(kwargs).items():
                span.set_attribute(f"mcp.{k}", v)
            result = fn(*args, **kwargs)
            span.set_attribute("mcp.success", True)
            return result
        except Exception as e:
            if span is not None:
                _set_span_error(span, e)
            raise
        finally:
            duration_ms = (time.perf_counter() - start) * 1000
            try:
                if span is not None:
                    span.set_attribute("mcp.duration_ms", duration_ms)
            except Exception:
                pass
            try:
                if span is not None:
                    span_cm.__exit__(None, None, None)
            except Exception:
                pass

    return _wrapped

