import asyncio
from dataclasses import dataclass
import time


@dataclass
class CommandResult:
    returncode: int | None
    stdout: str
    stderr: str

    @property
    def success(self) -> bool:
        return self.returncode == 0


async def run_command(command: str | bytes, cwd: str | None = None) -> CommandResult:
    """
    Run a command and capture stdout, stderr, and return code.

    Args:
        command: Command as string (if shell=True) or list of args
        shell: Whether to run through shell (use False for security)
        timeout: Optional timeout in seconds

    Returns:
        CommandResult with returncode, stdout, stderr
    """
    # Trace subprocess execution (no command args are recorded, only the "program").
    span = None
    span_cm = None
    try:
        tracer = None
        try:
            import importlib

            tracer = importlib.import_module("opentelemetry.trace").get_tracer("neptune_mcp")
        except Exception:
            tracer = None

        if tracer is not None:
            try:
                span_cm = tracer.start_as_current_span("subprocess.run")
                span = span_cm.__enter__()
                if isinstance(command, str):
                    program = command.strip().split(" ", 1)[0][:128] if command.strip() else ""
                    span.set_attribute("subprocess.program", program)
                    span.set_attribute("subprocess.arg_count", len(command.split()))
                else:
                    span.set_attribute("subprocess.program", "bytes")
                if cwd:
                    span.set_attribute("subprocess.cwd", cwd)
            except Exception:
                span = None

        start = time.perf_counter()
        proc = await asyncio.create_subprocess_shell(
        command,
        stderr=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        cwd=cwd,
        )

        stdout, stderr = await proc.communicate()
        duration_ms = (time.perf_counter() - start) * 1000
        if span is not None:
            try:
                span.set_attribute("subprocess.returncode", proc.returncode if proc.returncode is not None else -1)
                span.set_attribute("subprocess.success", proc.returncode == 0)
                span.set_attribute("duration_ms", duration_ms)
            except Exception:
                pass
    except Exception as e:
        if span is not None:
            try:
                span.set_attribute("error", True)
                span.record_exception(e)
            except Exception:
                pass
        raise
    finally:
        try:
            if span_cm is not None:
                span_cm.__exit__(None, None, None)
        except Exception:
            pass

    return CommandResult(returncode=proc.returncode, stdout=stdout.decode(), stderr=stderr.decode())
