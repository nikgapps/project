from __future__ import annotations

import json
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .errors import PipelineError


def _is_profile(path: Path) -> bool:
    return path.suffix.casefold() == ".prof"


def _ignore_profiles(_directory: str, names: list[str]) -> set[str]:
    return {name for name in names if Path(name).suffix.casefold() == ".prof"}


@dataclass
class UpgradeReport:
    upgraded_packages: list[str] = field(default_factory=list)
    file_only_packages: list[str] = field(default_factory=list)
    unavailable_packages: list[str] = field(default_factory=list)
    carried_forward_packages: list[str] = field(default_factory=list)
    updated_dependencies: list[str] = field(default_factory=list)
    carried_forward_files: list[str] = field(default_factory=list)
    ambiguous_dependencies: list[str] = field(default_factory=list)
    built_overlays: list[str] = field(default_factory=list)
    copied_files: int = 0

    def as_dict(self) -> dict[str, Any]:
        return {
            "schemaVersion": 1,
            "upgradedPackages": sorted(self.upgraded_packages),
            "fileOnlyPackages": sorted(self.file_only_packages),
            "unavailablePackages": sorted(self.unavailable_packages),
            "carriedForwardPackages": sorted(self.carried_forward_packages),
            "updatedDependencies": sorted(self.updated_dependencies),
            "carriedForwardFiles": sorted(self.carried_forward_files),
            "ambiguousDependencies": sorted(self.ambiguous_dependencies),
            "builtOverlays": sorted(self.built_overlays),
            "copiedFiles": self.copied_files,
        }


def _load_inventory(root: Path) -> dict[str, list[dict[str, Any]]]:
    inventory = root / "mustang.json"
    try:
        value = json.loads(inventory.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PipelineError(f"Cannot read Mustang inventory {inventory}: {exc}") from exc
    if not isinstance(value, dict):
        raise PipelineError(f"Mustang inventory must be an object: {inventory}")
    return value


def decode_builder_path(path: Path) -> str:
    return "/".join(path.parts).replace("___", "/").lstrip("/")


def encode_builder_path(path: str) -> Path:
    parts = Path(path).parts
    if len(parts) < 2:
        raise PipelineError(f"Firmware payload path has no install directory: {path!r}")
    # The first component is the source partition. The legacy builder selects
    # the target partition itself, so its repository paths intentionally omit it.
    return Path("___" + "___".join(parts[1:-1])) / parts[-1]


def _record_for_template(
    apk: Path, package_root: Path, baseline: dict[str, list[dict[str, Any]]]
) -> tuple[str, dict[str, Any]] | None:
    suffix = decode_builder_path(apk.relative_to(package_root))
    filename_matches: list[tuple[str, dict[str, Any]]] = []
    for package_name, records in baseline.items():
        for record in records:
            location = str(record.get("location", "")).replace("\\", "/")
            if location.endswith("/" + suffix):
                return package_name, record
            if Path(location).name == apk.name:
                filename_matches.append((package_name, record))
    return filename_matches[0] if len(filename_matches) == 1 else None


def _choose_target(
    records: list[dict[str, Any]], baseline_record: dict[str, Any]
) -> dict[str, Any] | None:
    usable = [
        record for record in records
        if str(record.get("location", "")).lower().endswith(".apk")
    ]
    if not usable:
        return None
    old_type = baseline_record.get("type")
    return min(
        usable,
        key=lambda record: (
            bool(record.get("isstub", False)),
            record.get("type") != old_type,
            str(record.get("location", "")),
        ),
    )


def _copy_firmware_directory(
    firmware_root: Path, record: dict[str, Any], package_output: Path
) -> int:
    location = str(record["location"]).replace("\\", "/")
    source_apk = firmware_root / Path(location)
    if not source_apk.is_file():
        raise PipelineError(f"Inventory references a missing APK: {source_apk}")
    source_directory = source_apk.parent
    count = 0
    for source in sorted(source_directory.rglob("*")):
        if (not source.is_file() or _is_profile(source)
                or any(part.endswith("_extracted") for part in source.parts)):
            continue
        source_location = Path(location).parent / source.relative_to(source_directory)
        destination = package_output / encode_builder_path(source_location.as_posix())
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        count += 1
    return count


class StableTreeUpgrader:
    """Create a legacy builder tree using payloads exclusively from a new image."""

    def upgrade(
        self,
        template_root: Path,
        baseline_firmware: Path,
        target_firmware: Path,
        output: Path,
        *,
        carry_forward_missing: bool = False,
    ) -> UpgradeReport:
        template_root = template_root.resolve()
        baseline_firmware = baseline_firmware.resolve()
        target_firmware = target_firmware.resolve()
        output = output.resolve()
        if not template_root.is_dir() or not target_firmware.is_dir():
            raise PipelineError("Template and target firmware directories must exist")
        if output.exists():
            raise PipelineError(f"Upgrade output already exists: {output}")
        if output == template_root or template_root in output.parents:
            raise PipelineError("Upgrade output must be outside the template tree")

        baseline = _load_inventory(baseline_firmware)
        target = _load_inventory(target_firmware)
        target_files: dict[str, list[Path]] = {}
        for candidate in sorted(target_firmware.rglob("*")):
            if not candidate.is_file() or candidate.name in {"mustang.json", "all_files.txt"}:
                continue
            if any(part.endswith("_extracted") or part == ".git" for part in candidate.parts):
                continue
            relative = candidate.relative_to(target_firmware).as_posix()
            try:
                builder_path = encode_builder_path(relative).as_posix()
            except PipelineError:
                continue
            target_files.setdefault(builder_path, []).append(candidate)
        report = UpgradeReport()
        output.mkdir(parents=True)
        for metadata_name in (".gitattributes", "README.md"):
            metadata = template_root / metadata_name
            if metadata.is_file():
                shutil.copy2(metadata, output / metadata_name)

        for appset in sorted(path for path in template_root.iterdir() if path.is_dir() and path.name != ".git"):
            for package in sorted(path for path in appset.iterdir() if path.is_dir()):
                membership = f"{appset.name}/{package.name}"
                destination = output / appset.name / package.name
                # Preserve the complete AppSet/package skeleton even when a
                # package is not shipped by the target firmware image.
                if carry_forward_missing:
                    shutil.copytree(package, destination, ignore=_ignore_profiles)
                else:
                    destination.mkdir(parents=True, exist_ok=True)
                template_apks = sorted(package.rglob("*.apk"))
                template_dependencies = sorted(
                    path for path in package.rglob("*")
                    if path.is_file() and path.suffix.casefold() not in {".apk", ".prof"}
                )
                copied = 0
                seen_targets: set[str] = set()
                replaced_apk_parents: set[Path] = set()
                for template_apk in template_apks:
                    match = _record_for_template(template_apk, package, baseline)
                    if not match:
                        continue
                    package_name, old_record = match
                    target_record = _choose_target(target.get(package_name, []), old_record)
                    if not target_record:
                        continue
                    location = str(target_record["location"])
                    if location in seen_targets:
                        continue
                    seen_targets.add(location)
                    if carry_forward_missing:
                        old_parent = destination / template_apk.parent.relative_to(package)
                        if old_parent not in replaced_apk_parents:
                            shutil.rmtree(old_parent)
                            replaced_apk_parents.add(old_parent)
                    copied += _copy_firmware_directory(target_firmware, target_record, destination)

                dependency_copied = 0
                for template_file in template_dependencies:
                    relative = template_file.relative_to(package)
                    builder_path = relative.as_posix()
                    matches = target_files.get(builder_path, [])
                    audit_path = f"{membership}/{builder_path}"
                    if len(matches) == 1:
                        destination_file = destination / relative
                        destination_file.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(matches[0], destination_file)
                        dependency_copied += 1
                        report.copied_files += 1
                        report.updated_dependencies.append(audit_path)
                    elif len(matches) > 1:
                        report.ambiguous_dependencies.append(audit_path)
                        if carry_forward_missing and destination.joinpath(relative).is_file():
                            report.carried_forward_files.append(audit_path)
                    elif carry_forward_missing and destination.joinpath(relative).is_file():
                        report.carried_forward_files.append(audit_path)

                if copied:
                    report.upgraded_packages.append(membership)
                    report.copied_files += copied
                    if carry_forward_missing and any(
                        destination.joinpath(apk.relative_to(package)).is_file() for apk in template_apks
                    ):
                        report.carried_forward_packages.append(membership)
                    continue

                if dependency_copied:
                    report.file_only_packages.append(membership)
                else:
                    report.unavailable_packages.append(membership)
                if carry_forward_missing and any(destination.rglob("*")):
                    report.carried_forward_packages.append(membership)

        (output / "upgrade-report.json").write_text(
            json.dumps(report.as_dict(), indent=2) + "\n", encoding="utf-8"
        )
        return report
