import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from nikgapps_registry.service import RegistryService


class FakeClient:
    api_url = "https://gitlab.com/api/v4"
    def __init__(self):
        self.uploads = []
        self.committed = None
    def read_repository_file(self, *args, **kwargs):
        return None
    def list_packages(self, *args, **kwargs):
        return []
    def upload_generic(self, project, name, version, artifact, **kwargs):
        data = artifact.read_bytes()
        self.uploads.append(data)
        return f"{self.api_url}/projects/{project}/packages/generic/{name}/{version}/{artifact.name}"
    def commit_directory(self, project, metadata, **kwargs):
        self.committed = json.loads((metadata / 'config-templates.json').read_text())


class ConfigTemplateTests(unittest.TestCase):
    def test_all_supported_templates_have_matching_versions_and_hashes(self):
        client = FakeClient()
        with tempfile.TemporaryDirectory() as directory:
            document = RegistryService(client).publish_config_templates('123', Path(directory))
        self.assertEqual(set(['10', '11', '12', '12.1', '13', '14', '15', '16', '17']), set(document['templates']))
        self.assertEqual('38', document['templates']['16']['version'])
        self.assertEqual('40', document['templates']['17']['version'])
        for entry in document['templates'].values():
            data = next(data for data in client.uploads if hashlib.sha256(data).hexdigest() == entry['template']['sha256'])
            self.assertEqual(len(data), entry['template']['size'])
            text = data.decode('utf-8')
            self.assertNotIn('\r', text)
            self.assertIn(f"Version={entry['version']}\n", text)
            self.assertIn(f"AndroidVersion={entry['androidVersion']}\n", text)
            self.assertIn('UseZipConfig=1\n', text)
        self.assertEqual(document, client.committed)
