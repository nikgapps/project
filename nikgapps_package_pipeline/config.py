from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .errors import PipelineError
from .models import PackageOverride
from .util import safe_path


def platform_api_for_android(android_version: str | int | float) -> int:
    value = str(android_version)
    known = {
        "10": 29, "11": 30, "12": 31, "12.0": 31, "12.1": 32,
        "13": 33, "14": 34, "15": 35, "16": 36, "17": 37,
    }
    if value in known:
        return known[value]
    try:
        major = int(float(value))
    except ValueError as exc:
        raise PipelineError(f"Unsupported Android version: {android_version!r}") from exc
    if major >= 13:
        return major + 20
    raise PipelineError(f"Unsupported Android version: {android_version!r}")


@dataclass
class PipelineConfig:
    schema_version: int = 1
    repository_name: str = "nikgapps-package-catalog"
    android_version: str = "16"
    platform_api: int = 36
    channel: str = "stable"
    architecture: str = "arm64-v8a"
    default_partition: str = "product"
    packages: dict[str, PackageOverride] = field(default_factory=dict)

    def override_for(self, appset: str, package: str) -> PackageOverride:
        raw = self.packages.get(f"{appset}/{package}", self.packages.get(package))
        if raw is None:
            return PackageOverride(default_partition=self.default_partition)
        return raw


def _override(value: dict[str, Any], default_partition: str) -> PackageOverride:
    accepted = {
        "id", "name", "primaryApk", "defaultPartition", "minApi", "maxApi",
        "architectures", "replaceable", "include", "exclude",
        "removeFiles", "removeOverlays", "privilegedPermissions",
        "cleanFlashOnly", "additionalInstallerScript", "validationScript",
        "addonIndex",
    }
    unknown = sorted(set(value) - accepted)
    if unknown:
        raise PipelineError(f"Unknown package override fields: {', '.join(unknown)}")
    primary = value.get("primaryApk")
    if primary:
        safe_path(primary)
    return PackageOverride(
        package_id=value.get("id"),
        name=value.get("name"),
        primary_apk=primary,
        default_partition=value.get("defaultPartition", default_partition),
        min_api=value.get("minApi"),
        max_api=value.get("maxApi"),
        architectures=value.get("architectures"),
        replaceable=value.get("replaceable", True),
        include=value.get("include"),
        exclude=value.get("exclude", []),
        remove_files=value.get("removeFiles"),
        remove_overlays=value.get("removeOverlays", []),
        privileged_permissions=value.get("privilegedPermissions", []),
        clean_flash_only=value.get("cleanFlashOnly"),
        additional_installer_script=value.get("additionalInstallerScript"),
        validation_script=value.get("validationScript"),
        addon_index=str(value.get("addonIndex", "09")),
    )


def load_config(
    path: Path | None, *, android_version: str, platform_api: int, channel: str
) -> PipelineConfig:
    if path is None:
        return PipelineConfig(
            android_version=android_version,
            platform_api=platform_api,
            channel=channel,
        )
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PipelineError(f"Cannot load configuration {path}: {exc}") from exc
    if raw.get("schemaVersion") != 1:
        raise PipelineError("Configuration schemaVersion must be 1")
    default_partition = raw.get("defaultPartition", "product")
    config = PipelineConfig(
        repository_name=raw.get("repositoryName", "nikgapps-package-catalog"),
        # Target platform values are operation inputs. Keeping them on the CLI
        # makes one package configuration reusable across Android releases.
        android_version=str(android_version),
        platform_api=int(platform_api),
        # The channel is an operation-time promotion target. A single config
        # must be reusable for stable, beta, and canary publication.
        channel=channel,
        architecture=raw.get("architecture", "arm64-v8a"),
        default_partition=default_partition,
    )
    packages = raw.get("packages", {})
    if not isinstance(packages, dict):
        raise PipelineError("Configuration packages must be an object")
    config.packages = {
        safe_path(key): _override(value, default_partition)
        for key, value in packages.items()
    }
    return config
