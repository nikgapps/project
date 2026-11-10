"""Publish a verified, atomic GitHub delivery mirror of a pinned GitLab snapshot."""
from __future__ import annotations

import argparse
import base64
import copy
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import time
from urllib.parse import quote, urlencode, urlparse

import requests

from nikgapps_package_pipeline.errors import PipelineError
from nikgapps_package_pipeline.gitlab import GitLabClient

DEFAULT_REPOSITORY = 'nikgapps/nikgapps-packages'
REQUIRED = {'catalog.json', 'appsets.json', 'builder-assets.json', 'config-templates.json', 'releases/index.json'}


def metadata_path(value: str) -> str:
    path = PurePosixPath(value)
    if path.is_absolute() or '..' in path.parts or '\\' in value or not value.endswith('.json'):
        raise PipelineError('Unsafe metadata path: ' + value)
    return value


def encoded(document) -> bytes:
    return (json.dumps(document, indent=2, ensure_ascii=False) + '\n').encode()


class GitLabSnapshot:
    def __init__(self, token: str, project: str = '85036487'):
        self.client = GitLabClient('https://gitlab.com', token)
        self.project = str(project)
        self.project_path = 'projects/' + quote(self.project, safe='')
        self.artifact_prefix = 'https://gitlab.com/api/v4/' + self.project_path + '/packages/generic/'

    def head(self) -> str:
        body, _ = self.client._request('GET', self.project_path + '/repository/branches/main')
        return json.loads(body)['commit']['id']

    def documents(self, commit: str) -> dict[str, dict]:
        result, page = {}, 1
        while True:
            body, _ = self.client._request('GET', self.project_path + '/repository/tree?' + urlencode(
                {'ref': commit, 'recursive': 'true', 'per_page': 100, 'page': page}))
            rows = json.loads(body)
            for row in rows:
                if row['type'] == 'blob' and row['path'].endswith('.json'):
                    path = metadata_path(row['path'])
                    raw = self.client.read_repository_file(self.project, path, branch=commit)
                    if raw is None:
                        raise PipelineError('Missing pinned metadata: ' + path)
                    result[path] = json.loads(raw)
            if len(rows) < 100:
                break
            page += 1
        if missing := REQUIRED - result.keys():
            raise PipelineError('Incomplete source snapshot: ' + ', '.join(sorted(missing)))
        return result

    def download(self, artifact: dict, path: Path) -> None:
        url = artifact['url']
        if not url.startswith(self.artifact_prefix):
            raise PipelineError('Artifact is outside the source package registry')
        # Never forward the GitLab token to redirected object storage.
        for _ in range(6):
            headers = {'PRIVATE-TOKEN': self.client.token} if urlparse(url).hostname == 'gitlab.com' else {}
            with requests.get(url, headers=headers, stream=True, allow_redirects=False, timeout=(20, 120)) as response:
                if response.status_code in (301, 302, 303, 307, 308):
                    from urllib.parse import urljoin
                    url = urljoin(url, response.headers['Location'])
                    if urlparse(url).scheme != 'https':
                        raise PipelineError('Unsafe artifact redirect')
                    continue
                if not response.ok:
                    raise PipelineError(f'Source artifact download failed: HTTP {response.status_code}')
                digest, size = hashlib.sha256(), 0
                with path.open('wb') as output:
                    for chunk in response.iter_content(1024 * 1024):
                        size += len(chunk)
                        if size > artifact['size']:
                            raise PipelineError('Artifact exceeds declared size')
                        digest.update(chunk)
                        output.write(chunk)
                if size != artifact['size'] or digest.hexdigest() != artifact['sha256']:
                    raise PipelineError('Source artifact checksum or size mismatch')
                return
        raise PipelineError('Too many artifact redirects')


class GitHubMirror:
    def __init__(self, token: str, repository: str = DEFAULT_REPOSITORY):
        if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repository):
            raise PipelineError('Invalid GitHub repository')
        self.repository = repository
        self.base = 'https://api.github.com/repos/' + repository
        self.session = requests.Session()
        self.session.headers.update(Authorization='Bearer ' + token, Accept='application/vnd.github+json',
                                    **{'X-GitHub-Api-Version': '2022-11-28'})
        self.releases = {}
        self.objects = None
        self.last_write = 0.0

    def request(self, method, path, *, allowed=(200, 201), **kwargs):
        if method != 'GET':
            time.sleep(max(0, 1.0 - (time.monotonic() - self.last_write)))
            self.last_write = time.monotonic()
        url = path if path.startswith('https://') else self.base + path
        if urlparse(url).hostname not in {'api.github.com', 'uploads.github.com'}:
            raise PipelineError('Untrusted GitHub API endpoint')
        response = self.session.request(method, url, timeout=(20, 180), **kwargs)
        if response.status_code not in allowed:
            # Never include request headers, credentials or signed redirect URLs.
            raise PipelineError(f'GitHub {method} failed: HTTP {response.status_code}; '
                                f'retry-after={response.headers.get("Retry-After", "not supplied")}')
        return response

    def load_objects(self):
        if self.objects is not None:
            return
        self.objects = {}
        page = 1
        while True:
            rows = self.request('GET', f'/releases?per_page=100&page={page}').json()
            for release in rows:
                if not release['tag_name'].startswith('registry-objects-'):
                    continue
                assets, asset_page = {}, 1
                while True:
                    files = self.request('GET', f'/releases/{release["id"]}/assets?per_page=100&page={asset_page}').json()
                    assets.update({row['name']: row for row in files})
                    if len(files) < 100:
                        break
                    asset_page += 1
                self.releases[release['tag_name']] = (release, assets)
                for name, asset in assets.items():
                    if re.fullmatch(r'[0-9a-f]{64}\.blob', name):
                        self.objects[name] = asset
            if len(rows) < 100:
                break
            page += 1

    def release(self, digest):
        self.load_objects()
        # Fill numbered releases instead of creating a release for every object.
        # This bounds content-generating API calls and respects 1,000 assets/release.
        for version in range(1, 10000):
            tag = f'registry-objects-v{version}'
            if tag not in self.releases:
                release = self.request('POST', '/releases', json={
                    'tag_name': tag, 'name': f'NikGapps registry objects {version}', 'prerelease': True,
                    'body': 'Immutable checksum-addressed NikGapps packages. Managed by the publication workflow.',
                    'make_latest': 'false'}).json()
                self.releases[tag] = (release, {})
            release, assets = self.releases[tag]
            if len(assets) < 1000:
                return release, assets
        raise PipelineError('GitHub registry release buckets are full')

    def find(self, artifact):
        self.load_objects()
        asset = self.objects.get(artifact['sha256'] + '.blob')
        if asset is not None:
            self.verify(asset, artifact)
        return asset

    @staticmethod
    def verify(asset, artifact):
        if (asset.get('state') != 'uploaded' or asset['size'] != artifact['size'] or
                asset.get('digest') != 'sha256:' + artifact['sha256']):
            raise PipelineError('Existing GitHub asset does not match source checksum/size')

    def upload(self, artifact, path):
        release, assets = self.release(artifact['sha256'])
        name = artifact['sha256'] + '.blob'
        if len(assets) >= 1000:
            raise PipelineError('GitHub asset bucket is full')
        label = '/'.join(urlparse(artifact['url']).path.split('/')[-3:])[:255]
        url = release['upload_url'].split('{', 1)[0] + '?' + urlencode({'name': name, 'label': label})
        with path.open('rb') as stream:
            asset = self.request('POST', url, data=stream, headers={'Content-Type': 'application/octet-stream'}).json()
        self.verify(asset, artifact)
        assets[name] = asset
        self.objects[name] = asset
        return asset

    def publish_documents(self, documents, provenance):
        ref = self.request('GET', '/git/ref/heads/main').json()['object']['sha']
        base = self.request('GET', '/git/commits/' + ref).json()['tree']['sha']
        entries = self.request('GET', '/git/trees/' + base + '?recursive=1').json()
        if entries.get('truncated'):
            raise PipelineError('GitHub metadata tree is truncated')
        previous = {row['path']: row['sha'] for row in entries['tree'] if row['type'] == 'blob'}
        documents = {**documents, 'mirror.json': provenance}
        changes = []
        if 'mirror.json' in previous:
            saved = self.request('GET', '/git/blobs/' + previous['mirror.json']).json()
            prior = json.loads(base64.b64decode(saved['content']))
            for name in set(prior.get('metadataPaths', [])) - set(provenance['metadataPaths']):
                metadata_path(name)
                if name in previous:
                    changes.append({'path': name, 'mode': '100644', 'type': 'blob', 'sha': None})
        for name, document in sorted(documents.items()):
            metadata_path(name)
            content = encoded(document)
            sha = hashlib.sha1(b'blob ' + str(len(content)).encode() + b'\0' + content).hexdigest()
            if previous.get(name) == sha:
                continue
            blob = self.request('POST', '/git/blobs', json={
                'content': base64.b64encode(content).decode(), 'encoding': 'base64'}).json()['sha']
            changes.append({'path': name, 'mode': '100644', 'type': 'blob', 'sha': blob})
        if not changes:
            return ref
        tree = self.request('POST', '/git/trees', json={'base_tree': base, 'tree': changes}).json()['sha']
        commit = self.request('POST', '/git/commits', json={'tree': tree, 'parents': [ref],
            'message': 'Mirror verified GitLab snapshot ' + provenance['sourceCommit']}).json()['sha']
        # Do not overwrite a concurrent publication or user edit.
        self.request('PATCH', '/git/refs/heads/main', json={'sha': commit, 'force': False})
        return commit


def mirror_snapshot(source, destination, work: Path):
    work.mkdir(parents=True, exist_ok=True)
    commit = source.head()
    documents = copy.deepcopy(source.documents(commit))
    artifacts, locations = {}, {}

    def visit(value):
        if isinstance(value, dict):
            url = value.get('url')
            if isinstance(url, str) and urlparse(url).hostname == 'gitlab.com' and 'sha256' in value:
                if (not re.fullmatch('[0-9a-f]{64}', value['sha256']) or
                    type(value.get('size')) is not int or not 0 <= value['size'] < 2 * 1024**3 or
                    not url.startswith(source.artifact_prefix)):
                    raise PipelineError('Invalid source artifact metadata')
                old = artifacts.setdefault(value['sha256'], copy.deepcopy(value))
                if old['size'] != value['size']:
                    raise PipelineError('Conflicting artifact sizes for checksum')
                locations.setdefault(value['sha256'], []).append(value)
            for child in value.values():
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)

    for document in documents.values():
        visit(document)
    uploaded = reused = 0
    for digest, artifact in sorted(artifacts.items()):
        asset = destination.find(artifact)
        if asset is None:
            temporary = work / (digest + '.part')
            try:
                source.download(artifact, temporary)
                asset = destination.upload(artifact, temporary)
                uploaded += 1
            finally:
                temporary.unlink(missing_ok=True)
        else:
            reused += 1
        for row in locations[digest]:
            row['url'] = f'https://api.github.com/repos/{destination.repository}/releases/assets/{asset["id"]}'
        print(f'Verified mirror object {digest[:12]} ({uploaded} uploaded, {reused} reused)', flush=True)
    if source.head() != commit:
        raise PipelineError('GitLab changed during mirror upload; rerun to publish the latest snapshot')
    provenance = {'schemaVersion': 1, 'source': 'gitlab', 'project': source.project, 'sourceCommit': commit,
                  'repository': destination.repository, 'metadataPaths': sorted(documents)}
    github_commit = destination.publish_documents(documents, provenance)
    receipt = {**provenance, 'githubCommit': github_commit, 'artifactCount': len(artifacts),
               'uploaded': uploaded, 'reused': reused}
    (work / 'mirror-receipt.json').write_bytes(encoded(receipt))
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', default='85036487')
    parser.add_argument('--repository', default=DEFAULT_REPOSITORY)
    parser.add_argument('--work', type=Path, required=True)
    args = parser.parse_args()
    gitlab = os.environ.get('GITLAB_TOKEN')
    github = os.environ.get('PACKAGES_GITHUB_TOKEN')
    if not gitlab or not github:
        raise SystemExit('GITLAB_TOKEN and PACKAGES_GITHUB_TOKEN are required')
    print(json.dumps(mirror_snapshot(GitLabSnapshot(gitlab, args.project),
        GitHubMirror(github, args.repository), args.work), indent=2))


if __name__ == '__main__':
    main()
