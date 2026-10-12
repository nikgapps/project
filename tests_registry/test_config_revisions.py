import hashlib
import unittest
import json
import tempfile
from pathlib import Path
from nikgapps_registry.service import RegistryService
from nikgapps_registry.config_revisions import release_definitions, attach_config_to_release
from nikgapps_registry.config_revisions import definition_fingerprint, next_config_version, template_with_version


class ConfigRevisionTests(unittest.TestCase):
    def test_removed_package_advances_revision_once(self):
        old = 'AndroidVersion=17\nVersion=40\nCore=1\n>>Initializer=1\n'
        new = 'AndroidVersion=17\nVersion=40\nCore=1\n'
        previous = {'version': '40', 'definitionFingerprint': definition_fingerprint(old)}
        fingerprint = definition_fingerprint(new)
        self.assertEqual(next_config_version(new, 40, previous, fingerprint), 41)
        previous.update(version='41', definitionFingerprint=fingerprint)
        self.assertEqual(next_config_version(new, 40, previous, fingerprint), 41)

    def test_legacy_template_migration_and_explicit_base_version(self):
        text = 'Version=40\nCore=1\n'
        previous = {'version': '40', 'template': {'sha256': hashlib.sha256(text.encode()).hexdigest()}}
        self.assertEqual(next_config_version(text, 40, previous, definition_fingerprint(text)), 40)
        self.assertEqual(next_config_version(text, 41, {}, definition_fingerprint(text)), 41)

    def test_package_constraint_changes_are_structural(self):
        text = 'Version=40\nCore=1\n'
        self.assertNotEqual(definition_fingerprint(text, {'partition':'product'}),
                            definition_fingerprint(text, {'partition':'system_ext'}))
        self.assertEqual(definition_fingerprint(text), definition_fingerprint(template_with_version(text, 41)))

    def test_published_revision_is_scoped_and_matches_uploaded_config(self):
        class Client:
            api_url = 'https://example.test/api/v4'
            document = None
            uploads = []
            def read_repository_file(self, *args, **kwargs):
                return json.dumps(self.document) if self.document else None
            def list_packages(self, *args, **kwargs): return []
            def upload_generic(self, project, name, version, artifact, **kwargs):
                self.uploads.append(artifact.read_bytes())
                return f'https://example.test/{name}/{version}'
        client = Client()
        service = RegistryService(client)
        with tempfile.TemporaryDirectory() as directory:
            metadata = Path(directory)
            original = {'packages':[{'id':'old'}], 'appSets':[]}
            client.document = service._update_config_templates('test', metadata, 'main', ['16', '17'],
                definitions={'16': original, '17': original})
            android16 = client.document['templates']['16'].copy()
            changed = {'packages':[], 'appSets':[]}
            client.document = service._update_config_templates('test', metadata, 'main', ['17'], definitions={'17':changed})
            entry = client.document['templates']['17']
            self.assertEqual(entry['version'], '41')
            self.assertEqual(client.document['templates']['16'], android16)
            uploaded = next(data for data in client.uploads if hashlib.sha256(data).hexdigest() == entry['template']['sha256'])
            self.assertIn(b'Version=41\n', uploaded)
            unchanged = service._update_config_templates('test', metadata, 'main', ['17'], definitions={'17':changed})
            self.assertEqual(unchanged['templates']['17']['version'], '41')

    def test_apk_updates_do_not_change_definition_fingerprint(self):
        with tempfile.TemporaryDirectory() as directory:
            metadata = Path(directory)
            (metadata/'releases').mkdir()
            (metadata/'releases/index.json').write_text(json.dumps({'latest':{'17':{'stable':{'arm64-v8a':'current'}}},
                'releases':[{'id':'current','manifest':'releases/current.json'}]}))
            release = {'packages':{'app':{'version':'one'}}, 'appSets':[]}
            (metadata/'releases/current.json').write_text(json.dumps(release))
            version = {'packageName':'com.example', 'android':{'minApi':29,'targetApi':35},
                'architectures':['arm64-v8a'], 'defaultPartition':'product'}
            newer = {**version, 'versionName':'2', 'android':{'minApi':29,'targetApi':36},'artifact':{'sha256':'new'}}
            (metadata/'catalog.json').write_text(json.dumps({'packages':[{'id':'app','name':'App','versions':{'one':version,'two':newer}}]}))
            before = release_definitions(metadata,'17')
            release['packages']['app']['version'] = 'two'
            (metadata/'releases/current.json').write_text(json.dumps(release))
            self.assertEqual(before, release_definitions(metadata,'17'))
            entry = {'version':'41','definitionFingerprint':'structure','template':{'url':'https://example.test/config'},
                'packageDefinitions':{'app':'hash'}, 'configSettings':['Version']}
            attach_config_to_release(metadata,'17','stable','arm64-v8a',entry)
            attached = json.loads((metadata/'releases/current.json').read_text())
            self.assertEqual(attached['configVersion'],'41')
            self.assertEqual(attached['packageDefinitions'],{'app':'hash'})


if __name__ == '__main__': unittest.main()
