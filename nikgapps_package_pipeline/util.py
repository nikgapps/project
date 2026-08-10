from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path, PurePosixPath
from typing import Any, Iterable

from .errors import PipelineError


def stable_id(value: str) -> str:
    separated = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", value)
    result = re.sub(r"[^a-z0-9]+", "_", separated.casefold()).strip("_")
    if not result:
        raise PipelineError(f"Cannot derive a stable ID from {value!r}")
    return result


def registry_component(value: str) -> str:
    """Normalize metadata for a GitLab generic-package coordinate."""
    result = re.sub(r"[^A-Za-z0-9._+-]+", "_", value).strip("._-+")
    if not result:
        raise PipelineError(f"Cannot create a registry component from {value!r}")
    return result


def safe_path(value: str) -> str:
    normalized = value.replace("\\", "/")
    path = PurePosixPath(normalized)
    if (
        not normalized
        or path.is_absolute()
        or ".." in path.parts
        or any(part in {"", "."} for part in path.parts)
    ):
        raise PipelineError(f"Unsafe relative path: {value!r}")
    return path.as_posix()


def decode_legacy_path(relative: Path) -> str:
    """Translate ___ separators while keeping paths partition-relative."""
    decoded = relative.as_posix().replace("___", "/").lstrip("/")
    return safe_path(decoded)


def resolve_inside(root: Path, relative: str) -> Path:
    target = root.joinpath(*PurePosixPath(safe_path(relative)).parts).resolve()
    resolved_root = root.resolve()
    if target != resolved_root and resolved_root not in target.parents:
        raise PipelineError(f"Path escapes source root: {relative!r}")
    return target


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def content_digest(files: Iterable[tuple[str, str]]) -> str:
    digest = hashlib.sha256()
    for path, checksum in sorted(files):
        digest.update(path.encode("utf-8"))
        digest.update(b"\0")
        digest.update(checksum.encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def json_data(value: Any, pretty: bool = True) -> bytes:
    return (
        json.dumps(
            value,
            indent=2 if pretty else None,
            separators=None if pretty else (",", ":"),
            ensure_ascii=False,
            sort_keys=False,
        )
        + "\n"
    ).encode("utf-8")
