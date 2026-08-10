from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from types import SimpleNamespace

from nikgapps_package_pipeline.consumer import (
    CatalogPackageSource,
    catalog_architecture,
    platform_api,
)
from nikgapps_package_pipeline.errors import PipelineError


def artifact(root: Path, name: str, payload_path: str, content: bytes) -> dict:
    path = root / f"{name}.zip"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr(f"payload/default/{payload_path}", content)
        archive.writestr("package.json", "{}")
    checksum = hashlib.sha256(path.read_bytes()).hexdigest()
    return {
        "url": path.as_uri(),
        "sha256": checksum,
        "size": path.stat().st_size,
    }


def built_artifact(root: Path, name: str, payload_path: str, content: bytes) -> dict:
    path = root / f"{name}.zip"
    parts = payload_path.split("/")
    archive_path = "___" + "___".join(parts[:-1]) + "/" + parts[-1]
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr(archive_path, content)
        archive.writestr("installer.sh", "find_install_mode\n")
        archive.writestr("uninstaller.sh", "uninstall_package\n")
        archive.writestr("package.json", json.dumps({"files": [{
            "path": payload_path, "archivePath": archive_path,
        }]}))
    checksum = hashlib.sha256(path.read_bytes()).hexdigest()
    return {"url": path.as_uri(), "sha256": checksum, "size": path.stat().st_size}


class ConsumerTests(unittest.TestCase):
    def test_android_api_and_architecture_mapping(self) -> None:
        self.assertEqual(platform_api("16"), 36)
        self.assertEqual(platform_api("12.1"), 32)
        self.assertEqual(catalog_architecture("arm64"), "arm64-v8a")

    def test_core_materializes_gms_and_standard_hidden_dependencies(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            artifacts = {
                "gms_core": artifact(
                    root, "gms", "priv-app/Gms/Gms.apk", b"apk"
                ),
                "gms_core_support_common": artifact(
                    root, "common", "etc/permissions/common.xml", b"common"
                ),
                "gms_core_support_standard": artifact(
                    root, "standard", "etc/sysconfig/variant.xml", b"standard"
                ),
                "gms_core_support_go": artifact(
                    root, "go", "etc/sysconfig/go.xml", b"go"
                ),
            }
            memberships = {
                "gms_core": ["Core/GmsCore", "CoreGo/GmsCore"],
                "gms_core_support_common": ["Core/ExtraFiles", "CoreGo/ExtraFilesGo"],
                "gms_core_support_standard": ["Core/ExtraFiles"],
                "gms_core_support_go": ["CoreGo/ExtraFilesGo"],
            }
            packages = []
            for package_id, artifact_data in artifacts.items():
                key = f"1-arm64-v8a-{package_id}"
                packages.append({
                    "id": package_id,
                    "legacy": {"memberships": memberships[package_id]},
                    "channels": {"stable": key},
                    "versions": {
                        key: {
                            "android": {"minApi": 29, "maxApi": None},
                            "architectures": [] if "support" in package_id else ["arm64-v8a"],
                            "artifact": artifact_data,
                        }
                    },
                })
            catalog = root / "catalog.json"
            catalog.write_text(json.dumps({"packages": packages}), encoding="utf-8")
            appsets = root / "appsets.json"
            appsets.write_text(json.dumps({
                "appSets": [{
                    "id": "core",
                    "name": "Core",
                    "packages": ["gms_core"],
                    "resolvedPackages": [
                        "gms_core",
                        "gms_core_support_common",
                        "gms_core_support_standard",
                    ],
                    "legacyPackageNames": {"gms_core": "GmsCore"},
                }]
            }), encoding="utf-8")
            requested = [SimpleNamespace(
                title="Core",
                package_list=[
                    SimpleNamespace(package_title="ExtraFiles"),
                    SimpleNamespace(package_title="GmsCore"),
                ],
            )]
            source = CatalogPackageSource(
                catalog.as_uri(), appsets.as_uri(), root / "cache"
            ).prepare(requested, "16", "arm64")
            self.assertTrue(
                (source / "Core" / "GmsCore" / "___priv-app___Gms" / "Gms.apk").is_file()
            )
            self.assertTrue(
                (source / "Core" / "ExtraFiles" / "___etc___permissions" / "common.xml").is_file()
            )
            self.assertTrue(
                (source / "Core" / "ExtraFiles" / "___etc___sysconfig" / "variant.xml").is_file()
            )
            self.assertFalse((source / "CoreGo").exists())

    def test_checksum_mismatch_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = root / "bad.zip"
            path.write_bytes(b"bad")
            source = CatalogPackageSource("", "", root / "cache")
            with self.assertRaisesRegex(PipelineError, "checksum mismatch"):
                source._artifact({"url": path.as_uri(), "sha256": "0" * 64})

    def test_materializes_prebuilt_package_zip(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            archive = built_artifact(root, "example", "priv-app/Example/App.apk", b"apk")
            archive_path = Path(archive["url"].removeprefix("file:///"))
            if not archive_path.exists():
                archive_path = root / "example.zip"
            output = root / "source"
            CatalogPackageSource._materialize(
                archive_path,
                {"id": "example", "legacy": {"memberships": ["Bundle/Example"]}},
                output,
                {"Bundle"},
            )
            self.assertEqual(
                (output / "Bundle" / "Example" / "___priv-app___Example" / "App.apk").read_bytes(),
                b"apk",
            )


if __name__ == "__main__":
    unittest.main()
