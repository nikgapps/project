"""Consume a published NikGapps catalog as a legacy builder source tree."""

from __future__ import annotations

import hashlib
import json
import logging
import os
import shutil
import tempfile
import urllib.error
import urllib.request
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any, Iterable

from .compat import encode_legacy_path
from .errors import PipelineError
from .config import platform_api_for_android
from .util import safe_path, stable_id

LOG = logging.getLogger(__name__)


def _message(value: str) -> None:
    print(f"[Registry] {value}")


def platform_api(android_version: str | int | float) -> int:
    return platform_api_for_android(android_version)


def catalog_architecture(builder_arch: str) -> str:
    aliases = {
        "arm64": "arm64-v8a",
        "arm64-v8a": "arm64-v8a",
        "arm": "armeabi-v7a",
        "armeabi-v7a": "armeabi-v7a",
        "x86": "x86",
        "x86_64": "x86_64",
    }
    try:
        return aliases[builder_arch.casefold()]
    except KeyError as exc:
        raise PipelineError(f"Unsupported package architecture: {builder_arch}") from exc


class CatalogPackageSource:
    """Resolve, cache, and materialize registry packages for existing builds."""

    def __init__(
        self,
        catalog_url: str,
        appsets_url: str,
        cache_directory: Path,
        *,
        channel: str = "stable",
        channel_overrides: dict[str, str] | None = None,
        token: str | None = None,
    ) -> None:
        self.catalog_url = catalog_url
        self.appsets_url = appsets_url
        self.cache_directory = cache_directory.resolve()
        self.channel = channel
        self.channel_overrides = channel_overrides or {}
        self.token = token

    def prepare(
        self,
        appsets: Iterable[Any],
        android_version: str | int | float,
        architecture: str,
    ) -> Path:
        appsets = list(appsets)
        selected_names = ", ".join(appset.title for appset in appsets)
        _message(
            f"Preparing AppSet source: {selected_names} "
            f"(channel={self.channel}, Android={android_version}, arch={architecture})"
        )
        _message("Reading catalog and AppSet metadata")
        catalog = self._read_json(self.catalog_url)
        appset_document = self._read_json(self.appsets_url)
        catalog_packages = {
            item["id"]: item for item in catalog.get("packages", [])
        }
        published_appsets = {
            item["id"]: item for item in appset_document.get("appSets", [])
        }
        requested: list[tuple[str, str]] = []
        selected_ids: list[str] = []
        for appset in appsets:
            appset_id = stable_id(appset.title)
            published = published_appsets.get(appset_id)
            if not published:
                raise PipelineError(f"AppSet {appset.title!r} is absent from appsets.json")
            legacy_names = published.get("legacyPackageNames", {})
            reverse_names = {
                name.casefold(): package_id for package_id, name in legacy_names.items()
            }
            for package in appset.package_list:
                package_id = reverse_names.get(package.package_title.casefold())
                # ExtraFiles and ExtraFilesGo are now hidden GmsCore dependencies.
                if package_id is None and package.package_title in {"ExtraFiles", "ExtraFilesGo"}:
                    continue
                if package_id is None:
                    raise PipelineError(
                        f"{appset.title}/{package.package_title} is absent from published AppSet metadata"
                    )
                if package_id not in selected_ids:
                    selected_ids.append(package_id)
            for package_id in published.get("resolvedPackages", []):
                if package_id in published.get("packages", []) and package_id not in selected_ids:
                    continue
                if any(selected == "gms_core" for selected in selected_ids) and package_id not in selected_ids:
                    selected_ids.append(package_id)
            requested.extend((appset.title, package_id) for package_id in selected_ids)

        public_ids = [
            package_id for package_id in selected_ids
            if not catalog_packages.get(package_id, {}).get("internal", False)
        ]
        internal_ids = [
            package_id for package_id in selected_ids
            if catalog_packages.get(package_id, {}).get("internal", False)
        ]
        _message(f"Selected packages: {', '.join(public_ids)}")
        if internal_ids:
            _message(
                "Automatically included hidden dependencies: "
                + ", ".join(internal_ids)
            )

        api = platform_api(android_version)
        arch = catalog_architecture(architecture)
        resolutions: list[tuple[str, dict[str, Any], dict[str, Any]]] = []
        for package_id in selected_ids:
            package = catalog_packages.get(package_id)
            if not package:
                raise PipelineError(f"Resolved package {package_id!r} is absent from catalog.json")
            version = self._resolve_version(package, api, arch)
            resolutions.append((package_id, package, version))
        fingerprint = hashlib.sha256(
            "\n".join(
                f"{package_id}:{version['artifact']['sha256']}"
                for package_id, _, version in resolutions
            ).encode("utf-8")
        ).hexdigest()[:16]
        source_root = (
            self.cache_directory / "sources" / str(android_version) / arch
            / self.channel / fingerprint
        )
        complete = source_root / ".complete"
        if complete.exists():
            _message(f"Using previously prepared source: {source_root}")
            LOG.info("Using prepared registry source %s", source_root)
            return source_root
        source_root.mkdir(parents=True, exist_ok=True)
        selected_appset_names = {appset.title for appset in appsets}
        for package_id, package, version in resolutions:
            _message(
                f"Resolving {package_id} -> "
                f"{package.get('channels', {}).get(self.channel, 'channel override')}"
            )
            archive = self._artifact(version["artifact"])
            self._materialize(
                archive,
                package,
                source_root,
                selected_appset_names,
            )
        complete.write_text(fingerprint + "\n", encoding="utf-8")
        _message(
            "Materialized registry packages into the legacy AppSet/Package layout"
        )
        _message(f"Prepared source is ready: {source_root}")
        LOG.info("Prepared registry source %s", source_root)
        return source_root

    def _resolve_version(
        self,
        package: dict[str, Any],
        api: int,
        architecture: str,
    ) -> dict[str, Any]:
        package_id = package["id"]
        channel = self.channel_overrides.get(package_id, self.channel)
        version_key = package.get("channels", {}).get(channel)
        if not version_key:
            raise PipelineError(f"Package {package_id} has no {channel!r} channel")
        version = package.get("versions", {}).get(version_key)
        if not version:
            raise PipelineError(f"Package {package_id} channel points to missing {version_key}")
        android = version.get("android", {})
        minimum = android.get("minApi")
        maximum = android.get("maxApi")
        if minimum is not None and api < int(minimum):
            raise PipelineError(f"Package {package_id} requires API {minimum}; build targets API {api}")
        if maximum is not None and api > int(maximum):
            raise PipelineError(f"Package {package_id} supports at most API {maximum}; build targets API {api}")
        architectures = version.get("architectures", [])
        if architectures and architecture not in architectures:
            raise PipelineError(
                f"Package {package_id} does not support {architecture}: {architectures}"
            )
        return version

    def _artifact(self, artifact: dict[str, Any]) -> Path:
        checksum = artifact["sha256"].casefold()
        destination = self.cache_directory / "artifacts" / f"{checksum}.zip"
        if destination.exists() and self._sha256(destination) == checksum:
            _message(f"Cache hit: {checksum[:12]}")
            return destination
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary = destination.with_suffix(".part")
        try:
            _message(f"Downloading: {artifact['url']}")
            with self._open(artifact["url"]) as response, temporary.open("wb") as output:
                shutil.copyfileobj(response, output, length=1024 * 1024)
            actual = self._sha256(temporary)
            if actual != checksum:
                raise PipelineError(
                    f"Artifact checksum mismatch for {artifact['url']}: expected {checksum}, got {actual}"
                )
            temporary.replace(destination)
            _message(f"Verified and cached: {checksum[:12]}")
        finally:
            temporary.unlink(missing_ok=True)
        return destination

    @staticmethod
    def _materialize(
        archive_path: Path,
        package: dict[str, Any],
        source_root: Path,
        selected_appsets: set[str],
    ) -> None:
        memberships = package.get("legacy", {}).get("memberships", [])
        applicable = [
            membership for membership in memberships
            if membership.split("/", 1)[0] in selected_appsets
        ]
        if not applicable:
            return
        if package.get("internal", False):
            targets = ", ".join(applicable)
            _message(
                f"Mapping hidden dependency {package['id']} to legacy {targets}; "
                "this is why ExtraFiles appears internally"
            )
        with zipfile.ZipFile(archive_path) as archive:
            try:
                descriptor = json.loads(archive.read("package.json"))
            except (KeyError, json.JSONDecodeError, UnicodeDecodeError) as exc:
                raise PipelineError(f"Invalid package descriptor in {archive_path}: {exc}") from exc
            file_rows = descriptor.get("files", [])
            if file_rows and all("archivePath" in row for row in file_rows):
                entries = [(archive.getinfo(row["archivePath"]), row["path"]) for row in file_rows]
            else:
                # Schema v1 payload archives remain readable during catalog migration.
                entries = [
                    (info, info.filename.removeprefix("payload/default/"))
                    for info in archive.infolist()
                    if info.filename.startswith("payload/default/") and not info.is_dir()
                ]
            for membership in applicable:
                appset, legacy_package = membership.split("/", 1)
                root = source_root / appset / legacy_package
                for info, payload in entries:
                    safe_path(payload)
                    destination = root / encode_legacy_path(payload)
                    resolved = destination.resolve()
                    if source_root.resolve() not in resolved.parents:
                        raise PipelineError(f"ZIP entry escapes source directory: {info.filename}")
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    with archive.open(info) as source, destination.open("wb") as output:
                        shutil.copyfileobj(source, output, length=1024 * 1024)

    def _read_json(self, url: str) -> dict[str, Any]:
        try:
            with self._open(url) as response:
                return json.loads(response.read().decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise PipelineError(f"Invalid JSON from {url}: {exc}") from exc

    def _open(self, url: str):
        headers = {}
        if self.token:
            headers["PRIVATE-TOKEN"] = self.token
        request = urllib.request.Request(url, headers=headers)
        try:
            return urllib.request.urlopen(request)
        except urllib.error.HTTPError as exc:
            raise PipelineError(f"Download failed with HTTP {exc.code}: {url}") from exc
        except urllib.error.URLError as exc:
            raise PipelineError(f"Download failed for {url}: {exc}") from exc

    @staticmethod
    def _sha256(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()


def channel_overrides_from_env(value: str | None) -> dict[str, str]:
    if not value:
        return {}
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError as exc:
        raise PipelineError(f"PACKAGE_CHANNEL_OVERRIDES must be JSON: {exc}") from exc
    if not isinstance(parsed, dict) or not all(
        isinstance(key, str) and isinstance(channel, str)
        for key, channel in parsed.items()
    ):
        raise PipelineError("PACKAGE_CHANNEL_OVERRIDES must be a string-to-string JSON object")
    return {stable_id(key): channel for key, channel in parsed.items()}
