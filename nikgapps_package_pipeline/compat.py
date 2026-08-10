from __future__ import annotations

import shutil
import zipfile
from pathlib import Path, PurePosixPath

from .errors import PipelineError
from .models import BuiltPackage
from .util import safe_path


def encode_legacy_path(path: str) -> Path:
    """Encode a partition-relative destination as one legacy directory."""
    normalized = safe_path(path)
    parts = PurePosixPath(normalized).parts
    if len(parts) < 2:
        raise PipelineError(f"Payload path has no parent directory: {path!r}")
    return Path("___" + "___".join(parts[:-1])) / parts[-1]


class LegacyCompatibilityExporter:
    """Materialize registry artifacts for the existing AppSet/Package builder."""

    def export(self, packages: list[BuiltPackage], output: Path) -> None:
        output = output.resolve()
        output.mkdir(parents=True, exist_ok=True)
        for package in packages:
            with zipfile.ZipFile(package.artifact_path) as archive:
                manifest = __import__("json").loads(archive.read("package.json"))
                payload_entries = {
                    row["archivePath"]: row["path"] for row in manifest["files"]
                }
                for source_name in package.source_names:
                    appset, legacy_package = source_name.split("/", 1)
                    package_root = output / appset / legacy_package
                    for entry, payload_path in payload_entries.items():
                        destination = package_root / encode_legacy_path(payload_path)
                        resolved_output = output.resolve()
                        resolved_destination = destination.resolve()
                        if resolved_output not in resolved_destination.parents:
                            raise PipelineError(f"Compatibility path escapes output: {entry}")
                        destination.parent.mkdir(parents=True, exist_ok=True)
                        with archive.open(entry) as source, destination.open("wb") as target:
                            shutil.copyfileobj(source, target, length=1024 * 1024)
