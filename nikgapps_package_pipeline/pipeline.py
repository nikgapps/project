from __future__ import annotations

import json
import logging
import zipfile
import hashlib
from xml.sax.saxutils import escape
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .apk import ApkInspector
from .archive import encode_builder_path, write_package_zip
from .config import PipelineConfig
from .errors import PipelineError
from .gitlab import GitLabClient
from .models import BuiltPackage, PayloadFile, SourcePackage
from .scanner import LegacyRepositoryScanner, primary_apk
from .util import (
    content_digest,
    file_sha256,
    json_data,
    safe_path,
    stable_id,
)

LOG = logging.getLogger(__name__)
ABI_ALIASES = {
    "arm64": "arm64-v8a",
    "arm64-v8a": "arm64-v8a",
    "armeabi-v7a": "armeabi-v7a",
    "x86": "x86",
    "x86_64": "x86_64",
    "riscv64": "riscv64",
}


def detect_architectures(files: list[PayloadFile], primary: PayloadFile | None) -> list[str]:
    found: set[str] = set()
    for item in files:
        for part in item.path.split("/"):
            if part.casefold() in ABI_ALIASES:
                found.add(ABI_ALIASES[part.casefold()])
    if primary:
        try:
            with zipfile.ZipFile(primary.source) as apk:
                for name in apk.namelist():
                    parts = name.split("/")
                    if len(parts) > 2 and parts[0] == "lib" and parts[1] in ABI_ALIASES:
                        found.add(ABI_ALIASES[parts[1]])
        except zipfile.BadZipFile as exc:
            raise PipelineError(f"Invalid APK ZIP: {primary.source}") from exc
    return sorted(found)


def _manifest(
    package_id: str,
    source: SourcePackage,
    files: list[PayloadFile],
    primary: PayloadFile | None,
    metadata: Any,
    architectures: list[str],
    content_sha: str,
    config: PipelineConfig,
) -> dict[str, Any]:
    minimum = source.override.min_api
    if minimum is None and metadata:
        minimum = metadata.min_api
    package_name = metadata.package_name if metadata else None
    try:
        from NikGapps.build.PackageConstants import PackageConstants
        default_removals = PackageConstants.get_package_deletes(package_name) if package_name else []
        default_clean = PackageConstants.get_package_clean_flash_rule(package_name) if package_name else False
        default_script = PackageConstants.get_package_script(source.name)
    except ImportError:
        default_removals, default_clean, default_script = [], False, None
    remove_files = source.override.remove_files
    if remove_files is None:
        remove_files = default_removals
    clean_flash = source.override.clean_flash_only
    if clean_flash is None:
        clean_flash = default_clean
    explicit_partitions = {"product", "system", "system_ext", "vendor"}
    file_rows = []
    for item in files:
        first = item.path.split("/", 1)[0]
        install_path = item.path if first in explicit_partitions else f"{source.override.default_partition}/{item.path}"
        file_rows.append({
            "path": item.path,
            "archivePath": encode_builder_path(item.path),
            "installPath": install_path,
            "sha256": item.sha256,
            "size": item.size,
            "type": _file_type(item.path, primary.path if primary else None),
        })
    generated_files: list[dict[str, Any]] = []
    existing_paths = {item.path for item in files}
    if package_name and source.override.privileged_permissions:
        permission_path = f"etc/permissions/{package_name}.xml"
        if permission_path in existing_paths:
            raise PipelineError(
                f"{source.appset}/{source.name}: generated privileged permission file "
                f"collides with source payload {permission_path}"
            )
        permission_text = "<permissions>\n" + "".join(
            f'    <privapp-permissions package="{escape(package_name)}">\n'
            f'        <permission name="{escape(permission)}" />\n'
            "    </privapp-permissions>\n"
            for permission in sorted(set(source.override.privileged_permissions))
        ) + "</permissions>\n"
        permission_bytes = permission_text.encode("utf-8")
        install_path = f"{source.override.default_partition}/{permission_path}"
        generated_files.append({"path": permission_path, "content": permission_text})
        file_rows.append({
            "path": permission_path,
            "archivePath": encode_builder_path(permission_path),
            "installPath": install_path,
            "sha256": hashlib.sha256(permission_bytes).hexdigest(),
            "size": len(permission_bytes),
            "type": "generatedPrivilegedPermission",
        })
    return {
        "schemaVersion": 1,
        "id": package_id,
        "name": source.override.name or source.name,
        "packageName": package_name,
        "versionName": metadata.version_name if metadata else f"content-{content_sha[:12]}",
        "versionCode": metadata.version_code if metadata else 0,
        "android": {
            "minApi": minimum,
            "targetApi": metadata.target_api if metadata else config.platform_api,
            "maxApi": source.override.max_api,
        },
        "architectures": architectures,
        "defaultPartition": source.override.default_partition,
        "apk": {
            "path": primary.path,
            "replaceable": source.override.replaceable,
        } if primary else None,
        "contentSha256": content_sha,
        "files": file_rows,
        "generatedFiles": generated_files,
        "install": {
            "format": "nikgapps-package-v1",
            "title": primary.source.stem if primary else source.name,
            "packageTitle": source.name,
            "payloadSize": sum((row["size"] + 1023) // 1024 for row in file_rows),
            "removeFiles": remove_files,
            "removeOverlays": source.override.remove_overlays,
            "privilegedPermissions": source.override.privileged_permissions,
            "cleanFlashOnly": clean_flash,
            "additionalInstallerScript": source.override.additional_installer_script
                if source.override.additional_installer_script is not None else default_script,
            "validationScript": source.override.validation_script,
            "addonIndex": source.override.addon_index,
        },
    }


def _file_type(path: str, primary_path: str | None) -> str:
    lower = path.casefold()
    if path == primary_path:
        return "primaryApk"
    if lower.endswith(".apk") and Path(path).name.casefold().startswith("split_"):
        return "splitApk"
    if lower.endswith(".apk") and ("/overlay/" in f"/{lower}" or lower.startswith("overlay/")):
        return "overlay"
    if lower.endswith(".apk"):
        return "apk"
    if "/permissions/" in f"/{lower}" and lower.endswith(".xml"):
        return "permission"
    if "/framework/" in f"/{lower}" or lower.endswith(".jar"):
        return "library"
    if lower.endswith(".so"):
        return "nativeLibrary"
    return "supportingFile"


def _build_contract_digest(files: list[PayloadFile], manifest: dict[str, Any]) -> str:
    digest = hashlib.sha256()
    digest.update(content_digest((item.path, item.sha256) for item in files).encode("ascii"))
    digest.update(b"\n")
    contract = {
        "defaultPartition": manifest["defaultPartition"],
        "apk": manifest["apk"],
        "install": manifest["install"],
        "files": [{"path": row["path"], "installPath": row["installPath"], "type": row["type"],
                   "sha256": row["sha256"], "size": row["size"]}
                  for row in manifest["files"]],
    }
    digest.update(json.dumps(contract, sort_keys=True, separators=(",", ":")).encode("utf-8"))
    return digest.hexdigest()


class MigrationPipeline:
    def __init__(
        self,
        scanner: LegacyRepositoryScanner,
        inspector: ApkInspector,
    ) -> None:
        self.scanner = scanner
        self.inspector = inspector

    def migrate(
        self,
        source_root: Path,
        output: Path,
        config: PipelineConfig,
        *,
        artifact_base_url: str,
        pretty: bool = True,
        package_filter: set[str] | None = None,
        overlay_root: Path | None = None,
    ) -> list[BuiltPackage]:
        source_root = source_root.resolve()
        output = output.resolve()
        if not source_root.is_dir():
            raise PipelineError(f"Source repository does not exist: {source_root}")
        if output == source_root or source_root in output.parents:
            raise PipelineError("Output must be outside the source repository")
        sources = self.scanner.discover(source_root, config)
        if overlay_root is not None:
            overlay_root = overlay_root.resolve()
            if not overlay_root.is_dir():
                raise PipelineError(f"Overlay directory does not exist: {overlay_root}")
        if package_filter:
            wanted = {value.casefold() for value in package_filter}
            include_gms_support = bool(
                wanted & {"gmscore", "core/gmscore", "corego/gmscore"}
            )
            sources = [
                source for source in sources
                if source.name.casefold() in wanted
                or f"{source.appset}/{source.name}".casefold() in wanted
                or (
                    include_gms_support
                    and f"{source.appset}/{source.name}" in {
                        "Core/ExtraFiles",
                        "CoreGo/ExtraFilesGo",
                    }
                )
            ]
            if not sources:
                raise PipelineError(
                    "No packages matched --package. Use a package name such as "
                    "GmsCore or an AppSet/Package value."
                )
        support_sources = {
            f"{source.appset}/{source.name}": source
            for source in sources
            if f"{source.appset}/{source.name}" in {
                "Core/ExtraFiles",
                "CoreGo/ExtraFilesGo",
            }
        }
        sources = [
            source for source in sources
            if f"{source.appset}/{source.name}" not in support_sources
        ]
        built_by_id: dict[str, BuiltPackage] = {}
        appsets: dict[str, list[str]] = defaultdict(list)
        for source in sources:
            files = self.scanner.payload(source)
            primary = primary_apk(source, files)
            metadata = self.inspector.inspect(primary.source) if primary else None
            if overlay_root is not None and float(config.android_version) >= 12.1:
                files = self._with_overlays(source, files, overlay_root)
            if primary and self._is_privileged(primary.path):
                detected = self.inspector.privileged_permissions(primary.source)
                source.override.privileged_permissions = sorted(set(
                    source.override.privileged_permissions + detected
                ))
                if metadata and source.override.privileged_permissions:
                    permission_path = f"etc/permissions/{metadata.package_name}.xml"
                    replaced = [item for item in files if item.path == permission_path]
                    if replaced:
                        files = [item for item in files if item.path != permission_path]
                        LOG.info(
                            "Replacing legacy privileged-permission XML in %s/%s",
                            source.appset,
                            source.name,
                        )
            package_id = source.override.package_id or stable_id(source.name)
            safe_path(package_id)
            if "/" in package_id:
                raise PipelineError(f"Package ID must be one path segment: {package_id!r}")
            payload_sha = content_digest((item.path, item.sha256) for item in files)
            architectures = (
                sorted(set(source.override.architectures))
                if source.override.architectures is not None
                else detect_architectures(files, primary)
            )
            provisional = _manifest(package_id, source, files, primary, metadata,
                                    architectures, payload_sha, config)
            content_sha = _build_contract_digest(files, provisional)
            version_code = metadata.version_code if metadata else 0
            architecture_key = f"-{config.architecture}" if architectures else ""
            version_key = (
                f"{version_code}{architecture_key}-{content_sha[:12]}"
                if metadata
                else f"content-{content_sha[:12]}{architecture_key}"
            )
            if any(char in version_key for char in "/\\"):
                raise PipelineError(f"Unsafe generated version key: {version_key!r}")
            previous = built_by_id.get(package_id)
            if previous:
                if previous.content_sha256 != content_sha:
                    raise PipelineError(
                        f"Package ID {package_id!r} has different payloads in "
                        f"{previous.source_names[0]} and {source.appset}/{source.name}; "
                        "configure distinct IDs"
                    )
                if source.appset not in previous.appsets:
                    previous.appsets.append(source.appset)
                previous.source_names.append(f"{source.appset}/{source.name}")
                appsets[source.appset].append(package_id)
                LOG.info("Reused identical package %s for %s", package_id, source.appset)
                continue
            manifest = _manifest(
                package_id, source, files, primary, metadata,
                architectures, content_sha, config,
            )
            artifact = output / "artifacts" / package_id / version_key / f"{package_id}.zip"
            write_package_zip(artifact, files, manifest, pretty=pretty)
            with zipfile.ZipFile(artifact) as archive:
                expected = encode_builder_path(primary.path) if primary else None
                if expected and expected not in archive.namelist():
                    raise PipelineError(f"Final archive is missing primary APK: {expected}")
            built = BuiltPackage(
                package_id=package_id,
                name=source.override.name or source.name,
                source_names=[f"{source.appset}/{source.name}"],
                appsets=[source.appset],
                version_key=version_key,
                metadata=metadata,
                min_api=source.override.min_api if source.override.min_api is not None
                else (metadata.min_api if metadata else None),
                target_api=metadata.target_api if metadata else config.platform_api,
                max_api=source.override.max_api,
                default_partition=source.override.default_partition,
                architectures=architectures,
                device_types=(source.override.device_types
                              if source.override.device_types is not None
                              else [config.default_device_type]),
                primary_apk=primary.path if primary else None,
                replaceable=source.override.replaceable,
                files=files,
                artifact_path=artifact,
                artifact_sha256=file_sha256(artifact),
                artifact_size=artifact.stat().st_size,
                content_sha256=content_sha,
                descriptor=manifest,
            )
            built_by_id[package_id] = built
            appsets[source.appset].append(package_id)
            LOG.info("Built %s %s", package_id, version_key)
        if support_sources:
            required = {"Core/ExtraFiles", "CoreGo/ExtraFilesGo"}
            if set(support_sources) != required:
                missing = ", ".join(sorted(required - set(support_sources)))
                raise PipelineError(
                    f"Cannot create hidden GmsCore support variants; missing {missing}"
                )
            support_packages = self._build_gms_support(
                support_sources,
                output,
                config,
                pretty,
            )
            for package in support_packages:
                if package.package_id in built_by_id:
                    raise PipelineError(f"Duplicate internal package ID: {package.package_id}")
                built_by_id[package.package_id] = package
            gms = built_by_id.get("gms_core")
            if not gms:
                raise PipelineError(
                    "ExtraFiles were found but GmsCore was not selected; migrate GmsCore "
                    "with its required support files"
                )
            gms.dependencies = [
                {
                    "id": "gms_core_extra_files",
                    "when": {"appSet": "core"},
                },
                {
                    "id": "gms_core_extra_files_go",
                    "when": {"appSet": "core_go"},
                },
            ]
        built_packages = sorted(built_by_id.values(), key=lambda value: value.package_id)
        self._write_metadata(output, built_packages, appsets, config, artifact_base_url, pretty)
        return built_packages

    @staticmethod
    def _is_privileged(path: str) -> bool:
        return "priv-app" in {part.casefold() for part in path.replace("\\", "/").split("/")}

    @staticmethod
    def _with_overlays(
        source: SourcePackage,
        files: list[PayloadFile],
        overlay_root: Path,
    ) -> list[PayloadFile]:
        directory = overlay_root / f"{source.name}Overlay"
        if not directory.is_dir():
            return files
        existing = {item.path for item in files}
        additions: list[PayloadFile] = []
        for apk in sorted(directory.rglob("*.apk")):
            path = f"overlay/{apk.name}"
            if path in existing:
                raise PipelineError(
                    f"{source.appset}/{source.name}: overlay collides with {path}"
                )
            existing.add(path)
            additions.append(PayloadFile(
                source=apk,
                path=path,
                sha256=file_sha256(apk),
                size=apk.stat().st_size,
            ))
        if additions:
            LOG.info("Embedded %d overlay(s) in %s/%s", len(additions), source.appset, source.name)
        return files + additions

    @staticmethod
    def _build_gms_support(
        sources: dict[str, SourcePackage],
        output: Path,
        config: PipelineConfig,
        pretty: bool,
    ) -> list[BuiltPackage]:
        normal_source = sources["Core/ExtraFiles"]
        go_source = sources["CoreGo/ExtraFilesGo"]
        scanner = LegacyRepositoryScanner()
        groups = [
            (
                "gms_core_extra_files",
                "ExtraFiles",
                scanner.payload(normal_source),
                ["Core/ExtraFiles"],
                ["Core"],
                normal_source,
            ),
            (
                "gms_core_extra_files_go",
                "ExtraFilesGo",
                scanner.payload(go_source),
                ["CoreGo/ExtraFilesGo"],
                ["CoreGo"],
                go_source,
            ),
        ]
        result: list[BuiltPackage] = []
        for package_id, name, files, source_names, appset_names, support_source in groups:
            if not files:
                continue
            payload_digest = content_digest((item.path, item.sha256) for item in files)
            manifest = _manifest(package_id, support_source, files, None, None, [],
                                 payload_digest, config)
            manifest.update({"name": name, "internal": True, "selectable": False})
            digest = _build_contract_digest(files, manifest)
            manifest["contentSha256"] = digest
            manifest["versionName"] = f"content-{digest[:12]}"
            version_key = f"content-{digest[:12]}"
            artifact = (
                output / "artifacts" / package_id / version_key / f"{package_id}.zip"
            )
            write_package_zip(artifact, files, manifest, pretty=pretty)
            result.append(BuiltPackage(
                package_id=package_id,
                name=name,
                source_names=source_names,
                appsets=appset_names,
                version_key=version_key,
                metadata=None,
                min_api=None,
                target_api=config.platform_api,
                max_api=None,
                default_partition=normal_source.override.default_partition,
                architectures=[],
                device_types=[config.default_device_type],
                primary_apk=None,
                replaceable=False,
                files=files,
                artifact_path=artifact,
                artifact_sha256=file_sha256(artifact),
                artifact_size=artifact.stat().st_size,
                content_sha256=digest,
                internal=True,
                descriptor=manifest,
            ))
            LOG.info("Built hidden dependency %s %s", package_id, version_key)
        return result

    @staticmethod
    def _write_metadata(
        output: Path,
        packages: list[BuiltPackage],
        appsets: dict[str, list[str]],
        config: PipelineConfig,
        base_url: str,
        pretty: bool,
    ) -> None:
        updated = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        catalog_packages: list[dict[str, Any]] = []
        for package in packages:
            url = (
                f"{base_url.rstrip('/')}/nikgapps-{package.package_id}/"
                f"{package.version_key}/{package.package_id}.zip"
            )
            version = package.catalog_version(
                url, config.android_version, config.source,
                config.architecture, config.default_device_type
            )
            catalog_packages.append({
                "id": package.package_id,
                "name": package.name,
                "selectable": not package.internal,
                "internal": package.internal,
                "legacy": {
                    "memberships": package.source_names,
                },
                "appSets": sorted({stable_id(name) for name in package.appsets}),
                "dependencies": package.dependencies,
                "channels": {
                    config.channel: package.version_key,
                },
                "versions": {
                    package.version_key: version,
                },
            })
        metadata = output / "metadata"
        metadata.mkdir(parents=True, exist_ok=True)
        catalog_path = metadata / "catalog.json"
        existing_catalog: dict[str, Any] = {}
        if catalog_path.exists():
            try:
                existing_catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                raise PipelineError(f"Cannot merge existing catalog {catalog_path}: {exc}") from exc
        existing_packages = {
            item["id"]: item for item in existing_catalog.get("packages", [])
        }
        for current in catalog_packages:
            previous = existing_packages.get(current["id"])
            if previous:
                current["appSets"] = sorted(set(previous.get("appSets", [])) | set(current["appSets"]))
                current["legacy"]["memberships"] = sorted(
                    set(previous.get("legacy", {}).get("memberships", []))
                    | set(current["legacy"]["memberships"])
                )
                versions = dict(previous.get("versions", {}))
                for version_key, current_version in current["versions"].items():
                    previous_version = versions.get(version_key)
                    if previous_version:
                        supported = set(previous_version.get("supportedAndroidVersions", []))
                        supported.update(current_version.get("supportedAndroidVersions", []))
                        current_version["supportedAndroidVersions"] = sorted(supported, key=float)
                        current_version["sources"] = sorted(
                            set(previous_version.get("sources", []))
                            | set(current_version.get("sources", []))
                        )
                versions.update(current["versions"])
                channels = dict(previous.get("channels", {}))
                new_version = current["channels"][config.channel]
                old_channel_version = channels.get(config.channel)
                same_legacy_platform = (
                    not existing_catalog
                    or str(existing_catalog.get("androidVersion")) == str(config.android_version)
                )
                if (same_legacy_platform and
                    config.channel == "stable"
                    and old_channel_version
                    and old_channel_version != new_version
                ):
                    channels["fallback"] = old_channel_version
                if same_legacy_platform:
                    channels[config.channel] = new_version
                current["versions"] = versions
                current["channels"] = channels
            existing_packages[current["id"]] = current
        legacy_android = str(existing_catalog.get("androidVersion", config.android_version))
        legacy_platform_api = int(existing_catalog.get("platformApi", config.platform_api))
        legacy_architecture = existing_catalog.get("architecture", config.architecture)
        legacy_channel = existing_catalog.get("channel", config.channel)
        catalog_path.write_bytes(json_data({
            "schemaVersion": 1,
            "updatedAt": updated,
            "defaults": existing_catalog.get("defaults", {
                "architectures": [config.architecture],
                "deviceTypes": [config.default_device_type],
            }),
            # Retain the original global pointer for schema-v1 clients. New
            # clients resolve Android/channel/release through releases/index.json.
            "androidVersion": legacy_android,
            "platformApi": legacy_platform_api,
            "architecture": legacy_architecture,
            "channel": legacy_channel,
            "packages": [
                existing_packages[key] for key in sorted(existing_packages)
            ],
        }, pretty))
        appsets_path = metadata / "appsets.json"
        existing_appsets: dict[str, Any] = {}
        if appsets_path.exists():
            try:
                previous_appsets = json.loads(appsets_path.read_text(encoding="utf-8"))
                existing_appsets = {
                    item["id"]: item for item in previous_appsets.get("appSets", [])
                }
            except (OSError, json.JSONDecodeError) as exc:
                raise PipelineError(f"Cannot merge existing AppSets {appsets_path}: {exc}") from exc
        generated_appsets = []
        for name, package_ids in sorted(appsets.items()):
            selected = list(dict.fromkeys(package_ids))
            resolved = MigrationPipeline._resolved_packages(name, selected, packages)
            legacy_names = {}
            for package_id in resolved:
                legacy_names[package_id] = next(
                    (
                        membership.split("/", 1)[1]
                        for package in packages
                        if package.package_id == package_id
                        for membership in package.source_names
                        if membership.split("/", 1)[0] == name
                    ),
                    package_id,
                )
            generated_appsets.append({
                "id": stable_id(name),
                "name": name,
                "packages": selected,
                "resolvedPackages": resolved,
                "legacyPackageNames": legacy_names,
            })
        if not existing_appsets or legacy_android == str(config.android_version):
            existing_appsets.update({item["id"]: item for item in generated_appsets})
        appsets_path.write_bytes(json_data({
            "schemaVersion": 1,
            "appSets": [
                existing_appsets[key] for key in sorted(existing_appsets)
            ],
        }, pretty))
        release = (
            metadata / "releases"
            / f"android-{config.android_version}-{config.architecture}.json"
        )
        release.parent.mkdir(parents=True, exist_ok=True)
        existing_release_packages: dict[str, Any] = {}
        if release.exists():
            try:
                previous_release = json.loads(release.read_text(encoding="utf-8"))
                existing_release_packages = dict(previous_release.get("packages", {}))
            except (OSError, json.JSONDecodeError) as exc:
                raise PipelineError(f"Cannot merge existing release lock {release}: {exc}") from exc
        existing_release_packages.update({
            package.package_id: {
                "version": package.version_key,
                "sha256": package.artifact_sha256,
            }
            for package in packages
        })
        release.write_bytes(json_data({
            "schemaVersion": 1,
            "createdAt": updated,
            "androidVersion": config.android_version,
            "platformApi": config.platform_api,
            "architecture": config.architecture,
            "channel": config.channel,
            "source": config.source,
            "packages": existing_release_packages,
        }, pretty))

        release_fingerprint_input = [
            str(config.android_version), config.channel, config.architecture, config.source,
            *(f"{package.package_id}:{package.version_key}"
              for package in sorted(packages, key=lambda item: item.package_id)),
        ]
        release_fingerprint = hashlib.sha256(
            "\n".join(release_fingerprint_input).encode("utf-8")
        ).hexdigest()[:8]
        release_id = f'{datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")}-{release_fingerprint}'
        release_manifest = (
            Path("releases") / f"android-{config.android_version}"
            / config.architecture / config.channel / f"{release_id}.json"
        )
        release_document = {
            "schemaVersion": 1,
            "id": release_id,
            "createdAt": updated,
            "androidVersion": config.android_version,
            "platformApi": config.platform_api,
            "architecture": config.architecture,
            "channel": config.channel,
            "source": config.source,
            "packages": {
                package.package_id: {"version": package.version_key}
                for package in packages
            },
            "appSets": generated_appsets,
        }
        (metadata / release_manifest).parent.mkdir(parents=True, exist_ok=True)
        (metadata / release_manifest).write_bytes(json_data(release_document, pretty))

        index_path = metadata / "releases" / "index.json"
        release_index: dict[str, Any] = {}
        if index_path.exists():
            try:
                release_index = json.loads(index_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                raise PipelineError(f"Cannot merge release history {index_path}: {exc}") from exc
        history = list(release_index.get("releases", []))
        release_summary = {
            "id": release_id,
            "androidVersion": config.android_version,
            "platformApi": config.platform_api,
            "architecture": config.architecture,
            "channel": config.channel,
            "source": config.source,
            "createdAt": updated,
            "manifest": release_manifest.as_posix(),
        }
        if not any(item.get("id") == release_id for item in history):
            history.append(release_summary)
        latest = dict(release_index.get("latest", {}))
        android_latest = dict(latest.get(str(config.android_version), {}))
        channel_latest = dict(android_latest.get(config.channel, {}))
        channel_latest[config.architecture] = release_id
        android_latest[config.channel] = channel_latest
        latest[str(config.android_version)] = android_latest
        index_path.write_bytes(json_data({
            "schemaVersion": 1,
            "updatedAt": updated,
            "latest": latest,
            "releases": history,
        }, pretty))

    @staticmethod
    def _resolved_packages(
        appset_name: str,
        package_ids: list[str],
        packages: list[BuiltPackage],
    ) -> list[str]:
        resolved = list(package_ids)
        appset_id = stable_id(appset_name)
        by_id = {package.package_id: package for package in packages}
        for package_id in package_ids:
            package = by_id[package_id]
            for dependency in package.dependencies:
                condition = dependency.get("when", {})
                if condition and condition.get("appSet") != appset_id:
                    continue
                dependency_id = dependency["id"]
                if dependency_id not in resolved:
                    resolved.append(dependency_id)
        return resolved

    @staticmethod
    def publish(
        packages: list[BuiltPackage],
        client: GitLabClient,
        project: str,
    ) -> dict[str, str]:
        urls: dict[str, str] = {}
        for package in packages:
            url = client.upload_generic(
                project,
                f"nikgapps-{package.package_id}",
                package.version_key,
                package.artifact_path,
            )
            urls[package.package_id] = url
            LOG.info("Published %s to %s", package.package_id, url)
        return urls
