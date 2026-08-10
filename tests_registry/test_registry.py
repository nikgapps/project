from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from nikgapps_package_pipeline.gitlab import GitLabPackage
from nikgapps_registry.service import RegistryService


class FakeClient:
    api_url = "https://gitlab.test/api/v4"

    def __init__(self) -> None:
        self.deleted: list[int] = []
        self.files = {
            "catalog.json": b'{"schemaVersion":1,"packages":[]}',
            "appsets.json": b'{"schemaVersion":1,"appSets":[]}',
        }

    def list_packages(self, project, *, package_type="generic"):
        return [GitLabPackage(7, "gms-core", "1", package_type)]

    def delete_package(self, project, package_id):
        self.deleted.append(package_id)

    def read_repository_file(self, project, path, *, branch="main"):
        return self.files.get(path)


class RegistryServiceTests(unittest.TestCase):
    def test_reset_deletes_every_listed_generic_package(self) -> None:
        client = FakeClient()
        deleted = RegistryService(client).reset("85036487")
        self.assertEqual([item.id for item in deleted], [7])
        self.assertEqual(client.deleted, [7])

    def test_seed_metadata_preserves_existing_local_files(self) -> None:
        client = FakeClient()
        with tempfile.TemporaryDirectory() as temporary:
            metadata = Path(temporary)
            (metadata / "catalog.json").write_bytes(b"local")
            RegistryService(client)._seed_metadata("85036487", "main", metadata)
            self.assertEqual((metadata / "catalog.json").read_bytes(), b"local")
            self.assertEqual(
                (metadata / "appsets.json").read_bytes(), client.files["appsets.json"]
            )

    def test_clear_is_restricted_to_work_metadata_child(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            work = Path(temporary) / "work"
            metadata = work / "metadata"
            metadata.mkdir(parents=True)
            (metadata / "catalog.json").write_text("{}", encoding="utf-8")
            RegistryService._safe_clear_metadata(metadata, work)
            self.assertFalse(metadata.exists())


if __name__ == "__main__":
    unittest.main()
