from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ApkMetadata:
    package_name: str
    version_name: str
    version_code: int
    min_api: int
    target_api: int


@dataclass(frozen=True)
class PayloadFile:
    source: Path
    path: str
    sha256: str
    size: int


@dataclass
class PackageOverride:
    package_id: str | None = None
    name: str | None = None
    primary_apk: str | None = None
    default_partition: str = "product"
    min_api: int | None = None
    max_api: int | None = None
    architectures: list[str] | None = None
    replaceable: bool = True
    include: list[str] | None = None
    exclude: list[str] = field(default_factory=list)
    remove_files: list[str] | None = None
    remove_overlays: list[str] = field(default_factory=list)
    privileged_permissions: list[str] = field(default_factory=list)
    clean_flash_only: bool | None = None
    additional_installer_script: str | None = None
    validation_script: str | None = None
    addon_index: str = "09"


@dataclass
class SourcePackage:
    appset: str
    name: str
    root: Path
    override: PackageOverride


@dataclass
class BuiltPackage:
    package_id: str
    name: str
    source_names: list[str]
    appsets: list[str]
    version_key: str
    metadata: ApkMetadata | None
    min_api: int | None
    target_api: int | None
    max_api: int | None
    default_partition: str
    architectures: list[str]
    primary_apk: str | None
    replaceable: bool
    files: list[PayloadFile]
    artifact_path: Path
    artifact_sha256: str
    artifact_size: int
    content_sha256: str
    internal: bool = False
    dependencies: list[dict[str, Any]] = field(default_factory=list)
    descriptor: dict[str, Any] = field(default_factory=dict)

    def catalog_version(self, artifact_url: str) -> dict[str, Any]:
        return {
            "versionName": self.metadata.version_name if self.metadata else self.version_key,
            "versionCode": self.metadata.version_code if self.metadata else 0,
            "packageName": self.metadata.package_name if self.metadata else None,
            "android": {
                "minApi": self.min_api,
                "targetApi": self.target_api,
                "maxApi": self.max_api,
            },
            "architectures": self.architectures,
            "defaultPartition": self.default_partition,
            "apk": {
                "path": self.primary_apk,
                "replaceable": self.replaceable,
            } if self.primary_apk else None,
            "artifact": {
                "url": artifact_url,
                "sha256": self.artifact_sha256,
                "size": self.artifact_size,
            },
            "contentSha256": self.content_sha256,
            "files": self.descriptor.get("files", []),
            "install": self.descriptor.get("install"),
        }
