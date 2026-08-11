from __future__ import annotations

import base64
import json
import urllib.error
import urllib.parse
import urllib.request
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .errors import PipelineError


@dataclass
class GitLabProject:
    id: int
    path_with_namespace: str
    web_url: str


@dataclass(frozen=True)
class GitLabPackage:
    id: int
    name: str
    version: str
    package_type: str


class GitLabClient:
    """Minimal GitLab API client with no dependency on the existing project."""

    def __init__(self, base_url: str, token: str) -> None:
        self.api_url = f"{base_url.rstrip('/')}/api/v4"
        self.token = token

    def _request(
        self,
        method: str,
        path: str,
        *,
        data: bytes | None = None,
        content_type: str | None = None,
    ) -> tuple[bytes, dict[str, str]]:
        headers = {"PRIVATE-TOKEN": self.token}
        if content_type:
            headers["Content-Type"] = content_type
        request = urllib.request.Request(
            f"{self.api_url}/{path.lstrip('/')}",
            data=data,
            headers=headers,
            method=method,
        )
        try:
            with urllib.request.urlopen(request) as response:
                return response.read(), dict(response.headers)
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise PipelineError(
                f"GitLab API {method} {path} failed with HTTP {exc.code}: {detail}"
            ) from exc
        except urllib.error.URLError as exc:
            raise PipelineError(f"Cannot reach GitLab API: {exc}") from exc

    def create_project(
        self,
        name: str,
        *,
        namespace_id: int | None = None,
        visibility: str = "public",
        description: str = "NikGapps package catalogs and registry artifacts",
    ) -> GitLabProject:
        payload: dict[str, Any] = {
            "name": name,
            "path": name,
            "visibility": visibility,
            "description": description,
            "initialize_with_readme": True,
        }
        if namespace_id is not None:
            payload["namespace_id"] = namespace_id
        body, _ = self._request(
            "POST",
            "projects",
            data=json.dumps(payload).encode("utf-8"),
            content_type="application/json",
        )
        result = json.loads(body)
        return GitLabProject(
            id=int(result["id"]),
            path_with_namespace=result["path_with_namespace"],
            web_url=result["web_url"],
        )

    def namespace_id(self, namespace: str) -> int:
        """Resolve a group/user namespace path to its numeric GitLab ID."""
        encoded = urllib.parse.quote(namespace.strip("/"), safe="")
        body, _ = self._request("GET", f"namespaces/{encoded}")
        result = json.loads(body)
        try:
            return int(result["id"])
        except (KeyError, TypeError, ValueError) as exc:
            raise PipelineError(
                f"GitLab did not return an ID for namespace {namespace!r}"
            ) from exc

    def create_project_in_namespace(
        self,
        name: str,
        namespace: str,
        *,
        visibility: str = "public",
        description: str = "NikGapps package catalogs and registry artifacts",
    ) -> GitLabProject:
        return self.create_project(
            name,
            namespace_id=self.namespace_id(namespace),
            visibility=visibility,
            description=description,
        )

    def upload_generic(
        self,
        project: str,
        package_name: str,
        version: str,
        artifact: Path,
        content_type: str = "application/zip",
    ) -> str:
        encoded_project = urllib.parse.quote(str(project), safe="")
        encoded_name = urllib.parse.quote(package_name, safe="")
        encoded_version = urllib.parse.quote(version, safe="")
        encoded_file = urllib.parse.quote(artifact.name, safe="")
        endpoint = (
            f"projects/{encoded_project}/packages/generic/{encoded_name}/"
            f"{encoded_version}/{encoded_file}"
        )
        payload = artifact.read_bytes()
        last_error: PipelineError | None = None
        for attempt in range(4):
            try:
                self._request(
                    "PUT",
                    endpoint,
                    data=payload,
                    content_type=content_type,
                )
                return f"{self.api_url}/{endpoint}"
            except PipelineError as exc:
                last_error = exc
                message = str(exc)
                retryable = any(
                    f"HTTP {status}" in message
                    for status in (429, 500, 502, 503, 504)
                ) or "Cannot reach GitLab API" in message
                if not retryable or attempt == 3:
                    raise
                delay = 2 ** attempt
                print(
                    f"[Registry] GitLab upload failed temporarily "
                    f"(attempt {attempt + 1}/4); retrying in {delay}s: {artifact.name}"
                )
                time.sleep(delay)
        assert last_error is not None
        raise last_error

    def read_repository_file(
        self, project: str, path: str, *, branch: str = "main"
    ) -> bytes | None:
        """Read a repository file, returning None when it does not exist."""
        encoded_project = urllib.parse.quote(str(project), safe="")
        encoded_path = urllib.parse.quote(path.strip("/"), safe="")
        query = urllib.parse.urlencode({"ref": branch})
        try:
            body, _ = self._request(
                "GET",
                f"projects/{encoded_project}/repository/files/{encoded_path}/raw?{query}",
            )
            return body
        except PipelineError as exc:
            if "HTTP 404" in str(exc):
                return None
            raise

    def list_packages(
        self, project: str, *, package_type: str = "generic"
    ) -> list[GitLabPackage]:
        encoded_project = urllib.parse.quote(str(project), safe="")
        packages: list[GitLabPackage] = []
        page = 1
        while True:
            query = urllib.parse.urlencode({
                "package_type": package_type,
                "per_page": 100,
                "page": page,
                "order_by": "created_at",
                "sort": "asc",
            })
            body, _ = self._request(
                "GET", f"projects/{encoded_project}/packages?{query}"
            )
            rows = json.loads(body)
            if not rows:
                break
            packages.extend(GitLabPackage(
                id=int(row["id"]),
                name=row["name"],
                version=row["version"],
                package_type=row["package_type"],
            ) for row in rows)
            if len(rows) < 100:
                break
            page += 1
        return packages

    def delete_package(self, project: str, package_id: int) -> None:
        encoded_project = urllib.parse.quote(str(project), safe="")
        endpoint = f"projects/{encoded_project}/packages/{int(package_id)}"
        last_error: PipelineError | None = None
        for attempt in range(6):
            try:
                self._request("DELETE", endpoint)
                return
            except PipelineError as exc:
                last_error = exc
                retryable = any(f"HTTP {status}" in str(exc) for status in (429, 500, 502, 503, 504))
                if not retryable or attempt == 5:
                    raise
                delay = min(30, 2 ** attempt)
                print(
                    f"[Registry] Delete rate-limited or temporarily unavailable "
                    f"(attempt {attempt + 1}/6); retrying in {delay}s"
                )
                time.sleep(delay)
        assert last_error is not None
        raise last_error

    def commit_directory(
        self,
        project: str,
        directory: Path,
        *,
        branch: str = "main",
        destination: str = "",
        message: str = "Update generated NikGapps package metadata",
    ) -> None:
        """Create or update a generated metadata tree in one GitLab commit."""
        encoded_project = urllib.parse.quote(str(project), safe="")
        query = urllib.parse.urlencode({
            "ref": branch,
            "recursive": "true",
            "per_page": "100",
        })
        body, _ = self._request(
            "GET", f"projects/{encoded_project}/repository/tree?{query}"
        )
        existing = {
            item["path"] for item in json.loads(body)
            if item.get("type") == "blob"
        }
        actions: list[dict[str, str]] = []
        for source in sorted(path for path in directory.rglob("*") if path.is_file()):
            relative = source.relative_to(directory).as_posix()
            target = f"{destination.strip('/')}/{relative}".lstrip("/")
            actions.append({
                "action": "update" if target in existing else "create",
                "file_path": target,
                "content": base64.b64encode(source.read_bytes()).decode("ascii"),
                "encoding": "base64",
            })
        if not actions:
            raise PipelineError(f"No metadata files found under {directory}")
        self._request(
            "POST",
            f"projects/{encoded_project}/repository/commits",
            data=json.dumps({
                "branch": branch,
                "commit_message": message,
                "actions": actions,
            }).encode("utf-8"),
            content_type="application/json",
        )
