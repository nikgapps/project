from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import zipfile
from pathlib import Path

from nikgapps_package_pipeline.apk import Aapt2Inspector, ApkInspector
from nikgapps_package_pipeline.config import PipelineConfig, load_config
from nikgapps_package_pipeline.cli import _load_env_file
from nikgapps_package_pipeline.compat import LegacyCompatibilityExporter, encode_legacy_path
from nikgapps_package_pipeline.errors import PipelineError
from nikgapps_package_pipeline.gitlab import GitLabClient
from nikgapps_package_pipeline.models import ApkMetadata
from nikgapps_package_pipeline.pipeline import MigrationPipeline
from nikgapps_package_pipeline.scanner import LegacyRepositoryScanner
from nikgapps_package_pipeline.util import decode_legacy_path, safe_path, stable_id


class FakeInspector(ApkInspector):
    def inspect(self, apk: Path) -> ApkMetadata:
        names = {
            "App.apk": ("com.example.app", "2.0", 200),
            "Shared.apk": ("com.example.shared", "3.0", 300),
            "Gms.apk": ("com.google.android.gms", "4.0", 400),
        }
        package, version, code = names[apk.name]
        return ApkMetadata(package, version, code, 29, 35)

    def privileged_permissions(self, apk: Path) -> list[str]:
        return ["android.permission.TEST_PRIVILEGED"]


def apk(path: Path, abi: str = "arm64-v8a") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr(f"lib/{abi}/libtest.so", b"native")


class UtilityTests(unittest.TestCase):
    def test_env_file_loads_token_without_overriding_existing_value(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / ".env"
            path.write_text(
                "# secret\nGITLAB_TOKEN='from-file'\nOTHER_VALUE=yes\n",
                encoding="utf-8",
            )
            with patch.dict("os.environ", {"GITLAB_TOKEN": "already-set"}, clear=True):
                self.assertTrue(_load_env_file(path))
                self.assertEqual(os.environ["GITLAB_TOKEN"], "already-set")
                self.assertEqual(os.environ["OTHER_VALUE"], "yes")

    def test_legacy_translation(self) -> None:
        path = Path("___priv-app___PrebuiltGmsCoreVic") / "Gms.apk"
        self.assertEqual(
            decode_legacy_path(path),
            "priv-app/PrebuiltGmsCoreVic/Gms.apk",
        )

    def test_stable_id_and_path_safety(self) -> None:
        self.assertEqual(stable_id("Google Play Store"), "google_play_store")
        for value in ("../bad", "/bad", r"..\bad"):
            with self.subTest(value=value), self.assertRaises(PipelineError):
                safe_path(value)
        self.assertEqual(
            encode_legacy_path("priv-app/Example/App.apk").as_posix(),
            "___priv-app___Example/App.apk",
        )

    def test_aapt_badging_parser(self) -> None:
        metadata = Aapt2Inspector.parse(
            "package: name='com.test' versionCode='42' versionName='1.2'\n"
            "sdkVersion:'29'\ntargetSdkVersion:'35'\n"
        )
        self.assertEqual(metadata, ApkMetadata("com.test", "1.2", 42, 29, 35))

    def test_aapt_inspector_tolerates_non_windows_text_bytes(self) -> None:
        output = (
            b"package: name='com.test' versionCode='42' versionName='1.2'\n"
            b"application-label:'bad\x8dlabel'\n"
            b"sdkVersion:'29'\ntargetSdkVersion:'35'\n"
        )
        with patch(
            "nikgapps_package_pipeline.apk.subprocess.run",
            return_value=subprocess.CompletedProcess([], 0, stdout=output, stderr=b""),
        ):
            metadata = Aapt2Inspector("aapt2").inspect(Path("test.apk"))
        self.assertEqual(metadata.package_name, "com.test")

    def test_aapt_inspector_reads_missing_minimum_from_manifest(self) -> None:
        badging = (
            b"package: name='com.test' versionCode='42' versionName='1.2'\n"
            b"targetSdkVersion:'35'\n"
        )
        manifest = (
            b"  E: uses-sdk (line=4)\n"
            b"    A: android:minSdkVersion(0x0101020c)=29\n"
            b"    A: android:targetSdkVersion(0x01010270)=35\n"
            b"  E: application\n"
        )
        with patch(
            "nikgapps_package_pipeline.apk.subprocess.run",
            side_effect=[
                subprocess.CompletedProcess([], 0, stdout=badging, stderr=b""),
                subprocess.CompletedProcess([], 0, stdout=manifest, stderr=b""),
            ],
        ):
            metadata = Aapt2Inspector("aapt2").inspect(Path("test.apk"))
        self.assertEqual(metadata.min_api, 29)

    def test_configuration_override(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "config.json"
            path.write_text(json.dumps({
                "schemaVersion": 1,
                "androidVersion": "16",
                "platformApi": 36,
                "packages": {
                    "Core/GmsCore": {
                        "id": "gms_core",
                        "defaultPartition": "system_ext",
                    }
                },
            }), encoding="utf-8")
            config = load_config(
                path, android_version="15", platform_api=35, channel="stable"
            )
            override = config.override_for("Core", "GmsCore")
            self.assertEqual(config.android_version, "15")
            self.assertEqual(config.platform_api, 35)
            self.assertEqual(config.channel, "stable")
            self.assertEqual(override.package_id, "gms_core")
            self.assertEqual(override.default_partition, "system_ext")

    def test_cli_channel_overrides_reusable_config(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "config.json"
            path.write_text(json.dumps({
                "schemaVersion": 1,
                "channel": "stable",
            }), encoding="utf-8")
            config = load_config(
                path, android_version="16", platform_api=36, channel="canary"
            )
            self.assertEqual(config.channel, "canary")

    def test_gitlab_metadata_commit_uses_create_and_update(self) -> None:
        class RecordingClient(GitLabClient):
            def __init__(self) -> None:
                super().__init__("https://gitlab.test", "token")
                self.requests: list[tuple[str, str, bytes | None]] = []

            def _request(self, method: str, path: str, *, data=None, content_type=None):
                self.requests.append((method, path, data))
                if method == "GET":
                    return b'[{"type":"blob","path":"catalog.json"}]', {}
                return b"{}", {}

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "catalog.json").write_text("{}", encoding="utf-8")
            (root / "appsets.json").write_text("{}", encoding="utf-8")
            client = RecordingClient()
            client.commit_directory("group/project", root)
            payload = json.loads(client.requests[-1][2])
            actions = {item["file_path"]: item["action"] for item in payload["actions"]}
            self.assertEqual(actions, {
                "appsets.json": "create",
                "catalog.json": "update",
            })

    def test_gitlab_resolves_namespace_before_project_creation(self) -> None:
        class RecordingClient(GitLabClient):
            def __init__(self) -> None:
                super().__init__("https://gitlab.test", "token")
                self.requests: list[tuple[str, str, bytes | None]] = []

            def _request(self, method: str, path: str, *, data=None, content_type=None):
                self.requests.append((method, path, data))
                if method == "GET":
                    return b'{"id":321}', {}
                return (
                    b'{"id":99,"path_with_namespace":"nikgapps/catalog",'
                    b'"web_url":"https://gitlab.test/nikgapps/catalog"}',
                    {},
                )

        client = RecordingClient()
        project = client.create_project_in_namespace("catalog", "nikgapps")
        self.assertEqual(project.id, 99)
        self.assertEqual(client.requests[0][1], "namespaces/nikgapps")
        create_payload = json.loads(client.requests[1][2])
        self.assertEqual(create_payload["namespace_id"], 321)

    def test_gitlab_repository_file_returns_content_or_none(self) -> None:
        class RecordingClient(GitLabClient):
            def _request(self, method: str, path: str, *, data=None, content_type=None):
                if "missing.json" in path:
                    raise PipelineError("failed with HTTP 404: missing")
                return b'{"schemaVersion":1}', {}

        client = RecordingClient("https://gitlab.test", "token")
        self.assertEqual(client.read_repository_file("1", "catalog.json"), b'{"schemaVersion":1}')
        self.assertIsNone(client.read_repository_file("1", "missing.json"))

    def test_gitlab_lists_and_deletes_generic_packages(self) -> None:
        class RecordingClient(GitLabClient):
            def __init__(self) -> None:
                super().__init__("https://gitlab.test", "token")
                self.deleted: list[str] = []

            def _request(self, method: str, path: str, *, data=None, content_type=None):
                if method == "GET":
                    return json.dumps([{
                        "id": 42, "name": "nikgapps-test", "version": "1",
                        "package_type": "generic",
                    }]).encode(), {}
                self.deleted.append(path)
                return b"", {}

        client = RecordingClient()
        packages = client.list_packages("85036487")
        self.assertEqual([(item.id, item.name) for item in packages], [(42, "nikgapps-test")])
        client.delete_package("85036487", packages[0].id)
        self.assertEqual(client.deleted, ["projects/85036487/packages/42"])

    def test_gitlab_upload_retries_transient_gateway_failure(self) -> None:
        class FlakyClient(GitLabClient):
            def __init__(self) -> None:
                super().__init__("https://gitlab.test", "token")
                self.attempts = 0

            def _request(self, method: str, path: str, *, data=None, content_type=None):
                self.attempts += 1
                if self.attempts < 3:
                    raise PipelineError("failed with HTTP 502: gateway")
                return b"", {}

        with tempfile.TemporaryDirectory() as temporary:
            artifact = Path(temporary) / "package.zip"
            artifact.write_bytes(b"zip")
            client = FlakyClient()
            with patch("nikgapps_package_pipeline.gitlab.time.sleep"):
                url = client.upload_generic("1", "test", "v1", artifact)
            self.assertEqual(client.attempts, 3)
            self.assertTrue(url.endswith("/test/v1/package.zip"))


class MigrationTests(unittest.TestCase):
    def make_tree(self, root: Path) -> None:
        package = root / "Bundle" / "Example"
        apk(package / "___priv-app___Example" / "App.apk")
        split = package / "___priv-app___Example" / "split_config.en.apk"
        apk(split)
        permission = package / "___etc___permissions" / "example.xml"
        permission.parent.mkdir(parents=True)
        permission.write_text("<permissions/>", encoding="utf-8")
        for appset in ("Core", "CoreGo"):
            apk(root / appset / "Shared" / "___priv-app___Shared" / "Shared.apk")
            apk(root / appset / "GmsCore" / "___priv-app___Gms" / "Gms.apk")
        for appset, package, value in (
            ("Core", "ExtraFiles", "standard"),
            ("CoreGo", "ExtraFilesGo", "go"),
        ):
            common = root / appset / package / "___etc___permissions" / "common.xml"
            common.parent.mkdir(parents=True)
            common.write_text("<common/>", encoding="utf-8")
            variant = root / appset / package / "___etc___sysconfig" / "variant.xml"
            variant.parent.mkdir(parents=True)
            variant.write_text(value, encoding="utf-8")

    def test_migration_catalog_appsets_and_file_only_package(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "source"
            output = Path(temporary) / "output"
            self.make_tree(root)
            config = PipelineConfig(android_version="16", platform_api=36, channel="stable")
            packages = MigrationPipeline(
                LegacyRepositoryScanner(), FakeInspector()
            ).migrate(
                root,
                output,
                config,
                artifact_base_url="https://gitlab.test/api/v4/projects/1/packages/generic",
            )
            self.assertEqual(
                {item.package_id for item in packages},
                {
                    "example",
                    "shared",
                    "gms_core",
                    "gms_core_support_common",
                    "gms_core_support_standard",
                    "gms_core_support_go",
                },
            )
            shared = next(item for item in packages if item.package_id == "shared")
            self.assertEqual(shared.appsets, ["Core", "CoreGo"])
            self.assertRegex(
                shared.version_key,
                r"^300-arm64-v8a-[0-9a-f]{12}$",
            )
            support = next(
                item for item in packages
                if item.package_id == "gms_core_support_common"
            )
            self.assertIsNone(support.primary_apk)
            self.assertTrue(support.internal)
            self.assertRegex(
                support.version_key,
                r"^content-[0-9a-f]{12}-arm64-v8a$",
            )
            with zipfile.ZipFile(next(item for item in packages if item.package_id == "example").artifact_path) as archive:
                self.assertIn("___priv-app___Example/App.apk", archive.namelist())
                self.assertIn(
                    "___priv-app___Example/split_config.en.apk",
                    archive.namelist(),
                )
                self.assertIn("installer.sh", archive.namelist())
                self.assertIn("uninstaller.sh", archive.namelist())
                installer = archive.read("installer.sh").decode()
                uninstaller = archive.read("uninstaller.sh").decode()
                self.assertIn("make_dir \"priv-app\"", installer)
                self.assertIn("delete_prop_lines \"$propFilePath\"", installer)
                self.assertIn("uninstall_package() {", uninstaller)
                self.assertIn("# Removing the updates and residue", uninstaller)
                self.assertIn(
                    "___etc___permissions/com.example.app.xml", archive.namelist()
                )
                permission_xml = archive.read(
                    "___etc___permissions/com.example.app.xml"
                ).decode()
                self.assertIn("android.permission.TEST_PRIVILEGED", permission_xml)
                descriptor = json.loads(archive.read("package.json"))
                self.assertEqual(descriptor["install"]["packageTitle"], "Example")
                expected_kib = sum((row["size"] + 1023) // 1024 for row in descriptor["files"])
                self.assertEqual(descriptor["install"]["payloadSize"], expected_kib)
                primary_row = next(row for row in descriptor["files"] if row["type"] == "primaryApk")
                self.assertEqual(primary_row["installPath"], "product/priv-app/Example/App.apk")
            appsets = json.loads((output / "metadata" / "appsets.json").read_text())
            core_go = next(item for item in appsets["appSets"] if item["name"] == "CoreGo")
            self.assertEqual(core_go["packages"], ["gms_core", "shared"])
            self.assertIn("gms_core_support_common", core_go["resolvedPackages"])
            self.assertIn("gms_core_support_go", core_go["resolvedPackages"])
            self.assertNotIn("gms_core_support_standard", core_go["resolvedPackages"])
            compatible = Path(temporary) / "compatible"
            LegacyCompatibilityExporter().export(packages, compatible)
            self.assertTrue(
                (
                    compatible / "Bundle" / "Example"
                    / "___priv-app___Example" / "App.apk"
                ).is_file()
            )

    def test_compiled_overlays_are_embedded_in_matching_package(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "source"
            output = Path(temporary) / "output"
            overlays = Path(temporary) / "overlays"
            apk(root / "Bundle" / "Example" / "___priv-app___Example" / "App.apk")
            overlay = overlays / "ExampleOverlay" / "ExampleOverlay.apk"
            overlay.parent.mkdir(parents=True)
            overlay.write_bytes(b"compiled-overlay")
            packages = MigrationPipeline(
                LegacyRepositoryScanner(), FakeInspector()
            ).migrate(
                root, output, PipelineConfig(android_version="16"),
                artifact_base_url="https://example.test",
                overlay_root=overlays,
            )
            with zipfile.ZipFile(packages[0].artifact_path) as archive:
                self.assertEqual(
                    archive.read("___overlay/ExampleOverlay.apk"),
                    b"compiled-overlay",
                )
                descriptor = json.loads(archive.read("package.json"))
                overlay_row = next(
                    row for row in descriptor["files"] if row["type"] == "overlay"
                )
                self.assertEqual(overlay_row["installPath"], "product/overlay/ExampleOverlay.apk")

    def test_matching_legacy_permission_xml_is_regenerated(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "source"
            package = root / "Bundle" / "Example"
            apk(package / "___priv-app___Example" / "App.apk")
            legacy = package / "___etc___permissions" / "com.example.app.xml"
            legacy.parent.mkdir(parents=True)
            legacy.write_text("<permissions><legacy /></permissions>", encoding="utf-8")
            unrelated = package / "___etc___permissions" / "unrelated.xml"
            unrelated.write_text("<permissions><unrelated /></permissions>", encoding="utf-8")
            packages = MigrationPipeline(
                LegacyRepositoryScanner(), FakeInspector()
            ).migrate(
                root, Path(temporary) / "output", PipelineConfig(),
                artifact_base_url="https://example.test",
            )
            with zipfile.ZipFile(packages[0].artifact_path) as archive:
                regenerated = archive.read(
                    "___etc___permissions/com.example.app.xml"
                ).decode()
                self.assertNotIn("<legacy", regenerated)
                self.assertIn("android.permission.TEST_PRIVILEGED", regenerated)
                self.assertIn("___etc___permissions/unrelated.xml", archive.namelist())

    def test_deterministic_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "source"
            self.make_tree(root)
            pipeline = MigrationPipeline(LegacyRepositoryScanner(), FakeInspector())
            first = pipeline.migrate(
                root, Path(temporary) / "one", PipelineConfig(),
                artifact_base_url="https://example.test",
            )
            second = pipeline.migrate(
                root, Path(temporary) / "two", PipelineConfig(),
                artifact_base_url="https://example.test",
            )
            self.assertEqual(
                [item.artifact_path.read_bytes() for item in first],
                [item.artifact_path.read_bytes() for item in second],
            )

    def test_package_filter_keeps_all_matching_appset_memberships(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "source"
            self.make_tree(root)
            packages = MigrationPipeline(
                LegacyRepositoryScanner(), FakeInspector()
            ).migrate(
                root,
                Path(temporary) / "output",
                PipelineConfig(),
                artifact_base_url="https://example.test",
                package_filter={"Shared"},
            )
            self.assertEqual(len(packages), 1)
            self.assertEqual(packages[0].appsets, ["Core", "CoreGo"])

    def test_catalog_preserves_history_and_sets_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "source"
            output = Path(temporary) / "output"
            self.make_tree(root)
            pipeline = MigrationPipeline(LegacyRepositoryScanner(), FakeInspector())
            pipeline.migrate(
                root,
                output,
                PipelineConfig(),
                artifact_base_url="https://example.test",
                package_filter={"Shared"},
            )
            catalog_path = output / "metadata" / "catalog.json"
            catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
            shared = catalog["packages"][0]
            current = shared["channels"]["stable"]
            shared["versions"]["older-version"] = {"artifact": {"sha256": "old"}}
            shared["channels"]["stable"] = "older-version"
            catalog_path.write_text(json.dumps(catalog), encoding="utf-8")
            pipeline.migrate(
                root,
                output,
                PipelineConfig(),
                artifact_base_url="https://example.test",
                package_filter={"Shared"},
            )
            merged = json.loads(catalog_path.read_text(encoding="utf-8"))
            shared = merged["packages"][0]
            self.assertEqual(shared["channels"]["stable"], current)
            self.assertEqual(shared["channels"]["fallback"], "older-version")
            self.assertIn("older-version", shared["versions"])

    def test_different_duplicate_package_requires_override(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "source"
            apk(root / "One" / "Shared" / "___app___Shared" / "Shared.apk")
            changed = root / "Two" / "Shared" / "___app___Shared" / "extra.xml"
            changed.parent.mkdir(parents=True)
            changed.write_text("different", encoding="utf-8")
            apk(changed.parent / "Shared.apk")
            with self.assertRaisesRegex(PipelineError, "distinct IDs"):
                MigrationPipeline(LegacyRepositoryScanner(), FakeInspector()).migrate(
                    root, Path(temporary) / "output", PipelineConfig(),
                    artifact_base_url="https://example.test",
                )

    def test_ambiguous_primary_apks_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "source"
            apk(root / "Bundle" / "Ambiguous" / "___app___One" / "App.apk")
            apk(root / "Bundle" / "Ambiguous" / "___app___Two" / "Shared.apk")
            with self.assertRaisesRegex(PipelineError, "primary APKs"):
                MigrationPipeline(LegacyRepositoryScanner(), FakeInspector()).migrate(
                    root, Path(temporary) / "output", PipelineConfig(),
                    artifact_base_url="https://example.test",
                )


if __name__ == "__main__":
    unittest.main()
