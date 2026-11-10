import copy
import hashlib
from pathlib import Path
import tempfile
import unittest

from nikgapps_package_pipeline.errors import PipelineError
from nikgapps_registry.github_mirror import mirror_snapshot, metadata_path, GitHubMirror


class Source:
    project = '85036487'
    artifact_prefix = 'https://gitlab.com/api/v4/projects/85036487/packages/generic/'

    def __init__(self):
        self.data = b'fixture package bytes'
        self.sha = hashlib.sha256(self.data).hexdigest()
        self.asset = {'url': self.artifact_prefix + 'example/v1/package.zip', 'sha256': self.sha, 'size': len(self.data)}
        self.docs = {'catalog.json': {'artifact': self.asset}, 'appsets.json': {}, 'builder-assets.json': {},
            'config-templates.json': {}, 'releases/index.json': {'latest': {'17': 'current'}},
            'releases/current.json': {'configTemplate': self.asset, 'sourceforge': {'status': 'published',
                'downloadUrl': 'https://sourceforge.net/projects/nikgapps/files/core.zip/download'}}}
        self.changed = False
        self.head_calls = 0
        self.fail = False

    def head(self):
        self.head_calls += 1
        return ('b' if self.changed and self.head_calls > 1 else 'a') * 40

    def documents(self, commit):
        return copy.deepcopy(self.docs)

    def download(self, artifact, path):
        path.write_bytes(self.data)
        if self.fail:
            raise PipelineError('checksum mismatch')


class Destination:
    repository = 'nikgapps/nikgapps-packages'

    def __init__(self):
        self.assets = {}
        self.published = None

    def find(self, artifact):
        return self.assets.get(artifact['sha256'])

    def upload(self, artifact, path):
        assert hashlib.sha256(path.read_bytes()).hexdigest() == artifact['sha256']
        asset = {'id': len(self.assets) + 1}
        self.assets[artifact['sha256']] = asset
        return asset

    def publish_documents(self, documents, provenance):
        self.published = (copy.deepcopy(documents), provenance)
        return 'c' * 40


class GitHubMirrorTests(unittest.TestCase):
    def test_existing_github_asset_must_have_matching_server_digest_and_size(self):
        source = Source()
        good = {'state': 'uploaded', 'size': source.asset['size'], 'digest': 'sha256:' + source.sha}
        GitHubMirror.verify(good, source.asset)
        for change in ({'state': 'starter'}, {'size': 0}, {'digest': None}, {'digest': 'sha256:' + '0' * 64}):
            with self.assertRaises(PipelineError):
                GitHubMirror.verify({**good, **change}, source.asset)

    def test_atomic_commit_removes_deleted_metadata_but_preserves_readme(self):
        import base64
        import json
        from types import SimpleNamespace
        client = GitHubMirror('fixture')
        calls = []
        def request(method, path, **kwargs):
            calls.append((method, path, kwargs))
            if path == '/git/ref/heads/main': result = {'object': {'sha': 'old-head'}}
            elif path == '/git/commits/old-head': result = {'tree': {'sha': 'old-tree'}}
            elif path.startswith('/git/trees/old-tree'): result = {'tree': [
                {'path': 'README.md', 'sha': 'readme', 'type': 'blob'},
                {'path': 'old.json', 'sha': 'old', 'type': 'blob'},
                {'path': 'mirror.json', 'sha': 'prior-mirror', 'type': 'blob'}]}
            elif path == '/git/blobs/prior-mirror': result = {'content': base64.b64encode(json.dumps({'metadataPaths': ['old.json']}).encode()).decode()}
            else: result = {'sha': 'new-object'}
            return SimpleNamespace(json=lambda: result)
        client.request = request
        client.publish_documents({'catalog.json': {}}, {'sourceCommit': 'a' * 40, 'metadataPaths': ['catalog.json']})
        tree = next(args['json']['tree'] for method, path, args in calls if method == 'POST' and path == '/git/trees')
        self.assertIn({'path': 'old.json', 'mode': '100644', 'type': 'blob', 'sha': None}, tree)
        self.assertFalse(any(row['path'] == 'README.md' for row in tree))
        self.assertEqual(('PATCH', '/git/refs/heads/main'), calls[-1][:2])
        self.assertFalse(calls[-1][2]['json']['force'])

    def test_deduplicates_verifies_and_publishes_metadata_last(self):
        source, target = Source(), Destination()
        with tempfile.TemporaryDirectory() as temporary:
            work = Path(temporary)
            receipt = mirror_snapshot(source, target, work)
            self.assertEqual(1, receipt['uploaded'])
            self.assertEqual(1, len(target.assets))
            self.assertFalse(list(work.glob('*.part')))
            documents = target.published[0]
            url = 'https://api.github.com/repos/nikgapps/nikgapps-packages/releases/assets/1'
            self.assertEqual(url, documents['catalog.json']['artifact']['url'])
            self.assertEqual(url, documents['releases/current.json']['configTemplate']['url'])
            self.assertEqual('published', documents['releases/current.json']['sourceforge']['status'])
            self.assertEqual(source.asset['url'], source.docs['catalog.json']['artifact']['url'])
            receipt = mirror_snapshot(source, target, work)
            self.assertEqual(0, receipt['uploaded'])
            self.assertEqual(1, receipt['reused'])

    def test_failed_download_never_publishes_and_cleans_partial_file(self):
        source, target = Source(), Destination()
        source.fail = True
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(PipelineError, 'checksum'):
                mirror_snapshot(source, target, Path(temporary))
            self.assertIsNone(target.published)
            self.assertFalse(list(Path(temporary).glob('*.part')))

    def test_source_change_during_upload_does_not_publish_stale_snapshot(self):
        source, target = Source(), Destination()
        source.changed = True
        with tempfile.TemporaryDirectory() as temporary, self.assertRaisesRegex(PipelineError, 'changed'):
            mirror_snapshot(source, target, Path(temporary))
        self.assertIsNone(target.published)

    def test_rejects_untrusted_registry_invalid_hash_and_oversized_assets(self):
        for changes in ({'url': 'https://gitlab.com/attacker/package.zip'}, {'sha256': 'invalid'}, {'size': 2 * 1024**3}):
            source, target = Source(), Destination()
            source.asset.update(changes)
            with tempfile.TemporaryDirectory() as temporary, self.assertRaises(PipelineError):
                mirror_snapshot(source, target, Path(temporary))
            self.assertIsNone(target.published)

    def test_rejects_conflicting_sizes_for_one_checksum(self):
        source, target = Source(), Destination()
        source.docs['icons.json'] = {'icon': {**source.asset, 'size': 999}}
        with tempfile.TemporaryDirectory() as temporary, self.assertRaisesRegex(PipelineError, 'Conflicting'):
            mirror_snapshot(source, target, Path(temporary))

    def test_metadata_paths_cannot_escape_repository(self):
        for path in ('../catalog.json', '/catalog.json', 'releases\\old.json', '.github/workflows/upload.yml'):
            with self.assertRaises(PipelineError):
                metadata_path(path)


if __name__ == '__main__':
    unittest.main()
