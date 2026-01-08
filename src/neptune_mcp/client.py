from dataclasses import dataclass
from typing import Any

import httpx
from neptune_common import (
    GetLogsResponse,
    GetProjectResponse,
    ListBucketKeysResponse,
    ListProjectsResponse,
    PostDeploymentResponse,
    PutProjectRequest,
    QueryDatabaseRequest,
)
import requests

from neptune_mcp.config import SETTINGS


def _trace_api_call(method: str, path: str):
    try:
        import importlib

        tracer = importlib.import_module("opentelemetry.trace").get_tracer("neptune_mcp")
        return tracer.start_as_current_span(f"neptune.api:{method.upper()} {path}")
    except Exception:
        class _Noop:
            def __enter__(self):  # noqa: D401
                return None

            def __exit__(self, exc_type, exc, tb):
                return False

        return _Noop()


@dataclass
class Client:
    api_base_url: str = SETTINGS.api_base_url

    def _mk_url(self, path: str) -> str:
        return f"{self.api_base_url}/{path.lstrip('/')}"

    def _get_headers(self) -> dict[str, str]:
        """Generate headers with bearer token if access_token is set."""
        headers = {}
        if SETTINGS.access_token is not None:
            headers["Authorization"] = f"Bearer {SETTINGS.access_token}"
        return headers

    def create_project(self, request: PutProjectRequest) -> None:
        with _trace_api_call("POST", "/project") as span:
            response = requests.post(
                self._mk_url("/project"), json=request.model_dump(mode="json"), headers=self._get_headers()
            )
            if span is not None:
                span.set_attribute("http.status_code", response.status_code)
            response.raise_for_status()

    def update_project(self, request: PutProjectRequest) -> None:
        with _trace_api_call("PUT", "/project/{name}") as span:
            response = requests.put(
                self._mk_url(f"/project/{request.name}"),
                json=request.model_dump(mode="json"),
                headers=self._get_headers(),
            )
            if span is not None:
                span.set_attribute("http.status_code", response.status_code)
            response.raise_for_status()

    def delete_project(self, project_name: str) -> None:
        with _trace_api_call("DELETE", "/project/{name}") as span:
            response = requests.delete(self._mk_url(f"/project/{project_name}"), headers=self._get_headers())
            if span is not None:
                span.set_attribute("http.status_code", response.status_code)
            response.raise_for_status()

    def get_project(self, project_name: str) -> GetProjectResponse | None:
        with _trace_api_call("GET", "/project/{name}") as span:
            response = requests.get(self._mk_url(f"/project/{project_name}"), headers=self._get_headers())
            if span is not None:
                span.set_attribute("http.status_code", response.status_code)
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return GetProjectResponse.model_validate(response.json())

    def create_deployment(self, project_name: str) -> PostDeploymentResponse:
        with _trace_api_call("POST", "/project/{name}/deploy") as span:
            response = requests.post(self._mk_url(f"/project/{project_name}/deploy"), headers=self._get_headers())
            if span is not None:
                span.set_attribute("http.status_code", response.status_code)
            response.raise_for_status()
            return PostDeploymentResponse.model_validate(response.json())

    async def create_deployment_async(self, project_name: str) -> PostDeploymentResponse:
        with _trace_api_call("POST", "/project/{name}/deploy") as span:
            async with httpx.AsyncClient() as client:
                response = await client.post(self._mk_url(f"/project/{project_name}/deploy"), headers=self._get_headers())
                if span is not None:
                    span.set_attribute("http.status_code", response.status_code)
                response.raise_for_status()
                return PostDeploymentResponse.model_validate(response.json())

    def get_deployment(self, project_name: str, revision: str | int = "latest") -> PostDeploymentResponse:
        with _trace_api_call("GET", "/project/{name}/deploy/{revision}") as span:
            response = requests.get(
                self._mk_url(f"/project/{project_name}/deploy/{revision}"),
                headers=self._get_headers(),
            )
            if span is not None:
                span.set_attribute("http.status_code", response.status_code)
            response.raise_for_status()
            return PostDeploymentResponse.model_validate(response.json())

    async def get_deployment_async(self, project_name: str, revision: str | int = "latest") -> PostDeploymentResponse:
        with _trace_api_call("GET", "/project/{name}/deploy/{revision}") as span:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self._mk_url(f"/project/{project_name}/deploy/{revision}"),
                    headers=self._get_headers(),
                )
                if span is not None:
                    span.set_attribute("http.status_code", response.status_code)
                response.raise_for_status()
                return PostDeploymentResponse.model_validate(response.json())

    def get_logs(self, project_name: str) -> GetLogsResponse:
        with _trace_api_call("GET", "/project/{name}/logs") as span:
            response = requests.get(self._mk_url(f"/project/{project_name}/logs"), headers=self._get_headers())
            if span is not None:
                span.set_attribute("http.status_code", response.status_code)
            response.raise_for_status()
            return GetLogsResponse.model_validate(response.json())

    def set_secret_value(self, project_name: str, key: str, value: str) -> None:
        # Do not record secret values in traces.
        with _trace_api_call("PUT", "/project/{name}/secret") as span:
            response = requests.put(
                self._mk_url(f"/project/{project_name}/secret"),
                json={"secret_name": key, "secret_string": value},
                headers=self._get_headers(),
            )
            if span is not None:
                span.set_attribute("http.status_code", response.status_code)
            response.raise_for_status()

    def list_bucket_keys(self, project_name: str, bucket_name: str) -> list[str]:
        with _trace_api_call("GET", "/project/{name}/bucket/{bucket}") as span:
            response = requests.get(
                self._mk_url(f"/project/{project_name}/bucket/{bucket_name}"),
                headers=self._get_headers(),
            )
            if span is not None:
                span.set_attribute("http.status_code", response.status_code)
            response.raise_for_status()
            return ListBucketKeysResponse.model_validate(response.json()).keys

    def get_bucket_object(self, project_name: str, bucket_name: str, key: str) -> bytes:
        with _trace_api_call("GET", "/project/{name}/bucket/{bucket}/object/{key}") as span:
            response = requests.get(
                self._mk_url(f"/project/{project_name}/bucket/{bucket_name}/object/{key}"),
                headers=self._get_headers(),
            )
            if span is not None:
                span.set_attribute("http.status_code", response.status_code)
            response.raise_for_status()
            return response.content

    def get_project_schema(self) -> dict[str, Any]:
        """Get the JSON schema that defines valid neptune.json configurations.

        Returns:
            JSON schema definition for project configuration (neptune.json)
        """
        with _trace_api_call("GET", "/schema/project") as span:
            response = requests.get(
                self._mk_url("/schema/project"),
                headers=self._get_headers(),
            )
            if span is not None:
                span.set_attribute("http.status_code", response.status_code)
            response.raise_for_status()
            return response.json()

    def list_projects(self) -> ListProjectsResponse:
        with _trace_api_call("GET", "/project") as span:
            response = requests.get(self._mk_url("/project"), headers=self._get_headers())
            if span is not None:
                span.set_attribute("http.status_code", response.status_code)
            response.raise_for_status()
            return ListProjectsResponse.model_validate(response.json())

    def query_database(self, project_name: str, database_name: str, request: QueryDatabaseRequest) -> dict[str, Any]:
        with _trace_api_call("POST", "/project/{name}/database/{db}/query") as span:
            response = requests.post(
                self._mk_url(f"/project/{project_name}/database/{database_name}/query"),
                json=request.model_dump(mode="json"),
                headers=self._get_headers(),
            )
            if span is not None:
                span.set_attribute("http.status_code", response.status_code)
            response.raise_for_status()
            return response.json()
