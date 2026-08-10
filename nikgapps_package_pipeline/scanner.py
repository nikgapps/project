from __future__ import annotations

import fnmatch
import logging
from pathlib import Path

from .config import PipelineConfig
from .errors import PipelineError
from .models import PayloadFile, SourcePackage
from .util import decode_legacy_path, file_sha256

LOG = logging.getLogger(__name__)


class LegacyRepositoryScanner:
    """Scanner isolated around the legacy AppSet/Package layout."""

    IGNORED_NAMES = {".gitattributes", "README.md"}

    def discover(self, root: Path, config: PipelineConfig) -> list[SourcePackage]:
        root = root.resolve()
        packages: list[SourcePackage] = []
        for appset_dir in sorted(p for p in root.iterdir() if p.is_dir() and p.name != ".git"):
            for package_dir in sorted(p for p in appset_dir.iterdir() if p.is_dir()):
                packages.append(
                    SourcePackage(
                        appset=appset_dir.name,
                        name=package_dir.name,
                        root=package_dir,
                        override=config.override_for(appset_dir.name, package_dir.name),
                    )
                )
        if not packages:
            raise PipelineError(f"No AppSet/Package directories found under {root}")
        return packages

    def payload(self, package: SourcePackage) -> list[PayloadFile]:
        result: list[PayloadFile] = []
        destination_paths: set[str] = set()
        for source in sorted(p for p in package.root.rglob("*") if p.is_file()):
            relative = source.relative_to(package.root)
            if source.name in self.IGNORED_NAMES or ".git" in relative.parts:
                continue
            raw = relative.as_posix()
            if package.override.include and not any(
                fnmatch.fnmatch(raw, rule) for rule in package.override.include
            ):
                continue
            if any(fnmatch.fnmatch(raw, rule) for rule in package.override.exclude):
                continue
            resolved = source.resolve()
            package_root = package.root.resolve()
            if package_root not in resolved.parents:
                raise PipelineError(f"{package.appset}/{package.name}: file escapes package root: {source}")
            destination = decode_legacy_path(relative)
            if destination in destination_paths:
                raise PipelineError(
                    f"{package.appset}/{package.name}: decoded path collision at {destination}"
                )
            destination_paths.add(destination)
            result.append(
                PayloadFile(
                    source=source,
                    path=destination,
                    sha256=file_sha256(source),
                    size=source.stat().st_size,
                )
            )
        if not result:
            raise PipelineError(f"{package.appset}/{package.name}: package contains no included files")
        return result


def primary_apk(package: SourcePackage, files: list[PayloadFile]) -> PayloadFile | None:
    apks = [item for item in files if item.path.casefold().endswith(".apk")]
    if not apks:
        return None
    if package.override.primary_apk:
        configured = decode_legacy_path(Path(package.override.primary_apk))
        matches = [
            item for item in apks
            if item.path == configured
            or item.source.relative_to(package.root).as_posix() == package.override.primary_apk
        ]
        if len(matches) != 1:
            raise PipelineError(
                f"{package.appset}/{package.name}: primaryApk "
                f"{package.override.primary_apk!r} does not match one included APK"
            )
        return matches[0]
    candidates = [
        item for item in apks
        if not item.source.name.casefold().startswith("split_")
        and "/lib/" not in f"/{item.path.casefold()}/"
        and "/overlay/" not in f"/{item.path.casefold()}/"
    ]
    if len(candidates) != 1:
        choices = ", ".join(item.path for item in candidates) or "none"
        raise PipelineError(
            f"{package.appset}/{package.name}: found {len(candidates)} possible "
            f"primary APKs ({choices}); configure primaryApk"
        )
    return candidates[0]
