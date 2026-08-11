from __future__ import annotations

import json
import hashlib
import shutil
import urllib.parse
from dataclasses import dataclass
from pathlib import Path

from nikgapps_package_pipeline.apk import Aapt2Inspector
from nikgapps_package_pipeline.config import load_config, platform_api_for_android
from nikgapps_package_pipeline.errors import PipelineError
from nikgapps_package_pipeline.gitlab import GitLabClient, GitLabPackage
from nikgapps_package_pipeline.pipeline import MigrationPipeline
from nikgapps_package_pipeline.scanner import LegacyRepositoryScanner


@dataclass(frozen=True)
class SyncRequest:
    source: Path
    work: Path
    config: Path
    project: str
    android_version: str
    architecture: str = "arm64-v8a"
    channel: str = "stable"
    platform_api: int | None = None
    metadata_branch: str = "main"
    package_filter: frozenset[str] = frozenset()
    fresh: bool = False
    pretty: bool = True
    overlays: Path | None = None
    busybox: Path | None = None
    builder_assets: Path | None = None


class RegistryService:
    """Owns the publish/reset lifecycle for an existing GitLab project."""

    def __init__(self, client: GitLabClient, *, aapt2: str = "aapt2") -> None:
        self.client = client
        self.aapt2 = aapt2

    def sync(self, request: SyncRequest) -> list[str]:
        source = request.source.resolve()
        if not source.is_dir():
            raise PipelineError(f"Legacy source directory does not exist: {source}")
        output = request.work.resolve()
        metadata = output / "metadata"
        if request.fresh and metadata.exists():
            self._safe_clear_metadata(metadata, output)
        if not request.fresh:
            if metadata.exists():
                self._safe_clear_metadata(metadata, output)
            self._seed_metadata(request.project, request.metadata_branch, metadata)

        api = request.platform_api or platform_api_for_android(request.android_version)
        config = load_config(
            request.config,
            android_version=request.android_version,
            platform_api=api,
            channel=request.channel,
        )
        config.architecture = request.architecture
        encoded = urllib.parse.quote(str(request.project), safe="")
        base_url = (
            f"{self.client.api_url}/projects/{encoded}/packages/generic"
        )
        pipeline = MigrationPipeline(
            LegacyRepositoryScanner(), Aapt2Inspector(self.aapt2)
        )
        packages = pipeline.migrate(
            source,
            output,
            config,
            artifact_base_url=base_url,
            pretty=request.pretty,
            package_filter=set(request.package_filter) or None,
            overlay_root=request.overlays,
        )
        existing_packages = self.client.list_packages(request.project, package_type="generic")
        existing = {
            (item.name, item.version)
            for item in existing_packages
        }
        pending = [
            package for package in packages
            if (f"nikgapps-{package.package_id}", package.version_key) not in existing
        ]
        urls = pipeline.publish(pending, self.client, request.project)
        for package in packages:
            urls.setdefault(
                package.package_id,
                f"{base_url}/nikgapps-{package.package_id}/"
                f"{package.version_key}/{package.package_id}.zip",
            )
        if request.builder_assets is not None and request.busybox is not None:
            generated_assets = output / "builder-assets"
            generated_assets.mkdir(parents=True, exist_ok=True)
            try:
                # The bundled niklibrary may predate the target platform. Use
                # the same local compatibility registration as overlay builds
                # before NikGappsConfig creates Overlay/Manifest objects.
                from NikGapps.overlay_control import register_android_platform
                from NikGapps.config.NikGappsConfig import NikGappsConfig
                register_android_platform(request.android_version)
                full_config = NikGappsConfig(request.android_version).get_nikgapps_config()
            except Exception as exc:
                raise PipelineError(f"Cannot generate full NikGapps configuration: {exc}") from exc
            config_template = generated_assets / "nikgapps.config"
            config_template.write_text(full_config, encoding="utf-8", newline="\n")
            assets = self._builder_assets(
                request.builder_assets.resolve(), request.busybox.resolve(), config_template)
            published_assets: dict[str, dict[str, str | int]] = {}
            for key, source in assets.items():
                digest = self._sha256(source)
                version = digest[:16]
                package_name = f"nikgapps-builder-{self._asset_id(key)}"
                url = f"{base_url}/{package_name}/{version}/{source.name}"
                if (package_name, version) not in existing:
                    url = self.client.upload_generic(
                        request.project, package_name, version, source,
                        content_type="application/octet-stream",
                    )
                published_assets[key] = {
                    "url": url, "sha256": digest, "size": source.stat().st_size,
                }
            (metadata / "builder-assets.json").write_text(json.dumps({
                "schemaVersion": 1, "assets": published_assets,
            }, indent=2) + "\n", encoding="utf-8")
        (output / "published-urls.json").write_text(
            json.dumps(urls, indent=2) + "\n", encoding="utf-8"
        )
        self.client.commit_directory(
            request.project,
            metadata,
            branch=request.metadata_branch,
            message=(
                f"Update NikGapps {request.android_version} "
                f"{request.architecture} {request.channel} registry metadata"
            ),
        )
        return urls

    @staticmethod
    def _sha256(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    @staticmethod
    def _asset_id(key: str) -> str:
        return "".join(character if character.isalnum() else "-" for character in key.lower()).strip("-")

    @staticmethod
    def _builder_assets(directory: Path, busybox: Path, config_template: Path) -> dict[str, Path]:
        names = {
            "META-INF/com/google/android/update-binary": "magisk-update-binary.sh",
            "afzc/debloater.config": "debloater.config",
            "changelog.yaml": "changelogs.yaml",
            "common/addon.sh": "addon.sh",
            "common/functions.sh": "functions.sh",
            "common/header.sh": "header.sh",
            "common/mtg_mount.sh": "mtg_mount.sh",
            "common/mount.sh": "mount.sh",
            "common/nikgapps_functions.sh": "nikgapps_functions.sh",
            "common/unmount.sh": "unmount.sh",
            "@template/customize.sh": "customize.sh",
            "module.prop": "module.prop",
        }
        result = {key: directory / name for key, name in names.items()}
        result["@template/nikgapps.config"] = config_template
        result["busybox"] = busybox
        missing = [f"{key}: {path}" for key, path in result.items() if not path.is_file()]
        if missing:
            raise PipelineError("Missing builder assets: " + "; ".join(missing))
        return result

    def registry_packages(self, project: str) -> list[GitLabPackage]:
        return self.client.list_packages(project, package_type="generic")

    def reset(self, project: str) -> list[GitLabPackage]:
        packages = self.registry_packages(project)
        for package in packages:
            self.client.delete_package(project, package.id)
        return packages

    def _seed_metadata(self, project: str, branch: str, directory: Path) -> None:
        core = ("catalog.json", "appsets.json", "builder-assets.json", "releases/index.json")
        seeded: dict[str, bytes] = {}
        for relative in core:
            target = directory / relative
            if target.exists():
                seeded[relative] = target.read_bytes()
                continue
            remote = self.client.read_repository_file(project, relative, branch=branch)
            if remote is not None:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(remote)
                seeded[relative] = remote
        index_bytes = seeded.get("releases/index.json")
        if index_bytes is None:
            return
        try:
            index = json.loads(index_bytes)
            manifests = {
                item["manifest"] for item in index.get("releases", [])
                if isinstance(item, dict) and isinstance(item.get("manifest"), str)
            }
        except (json.JSONDecodeError, TypeError) as exc:
            raise PipelineError(f"Cannot parse existing release index: {exc}") from exc
        for relative in sorted(manifests):
            target = directory / relative
            if target.exists():
                continue
            remote = self.client.read_repository_file(project, relative, branch=branch)
            if remote is not None:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(remote)

    @staticmethod
    def _safe_clear_metadata(metadata: Path, output: Path) -> None:
        if metadata.resolve().parent != output.resolve():
            raise PipelineError(f"Refusing to clear unexpected path: {metadata}")
        shutil.rmtree(metadata)
