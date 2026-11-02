"""Publish small app icons without changing catalog definitions or release metadata.

python -m nikgapps_registry.icons --work D:/workspace/artifacts/nikgapps-icons --publish
Icons are sourced from official Google Play listing metadata. Unlisted components
remain absent so clients can use their standard fallback. Existing icons survive
partial source failures; immutable Generic Registry assets are reused by hash.
"""
from __future__ import annotations
import argparse
import concurrent.futures
import hashlib
import html
import json
import os
import re
import subprocess
import zipfile
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from nikgapps_package_pipeline.cli import _load_default_env
from nikgapps_package_pipeline.gitlab import GitLabClient

MAX_ICON_BYTES = 512 * 1024

def image_extension(data: bytes) -> str:
    if data.startswith(b"\x89PNG\r\n\x1a\n"): return "png"
    if data.startswith(b"\xff\xd8\xff"): return "jpg"
    if data.startswith(b"RIFF") and data[8:12] == b"WEBP": return "webp"
    raise ValueError("Unsupported icon image")

def download(url: str, limit: int) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=25) as response:
        data = response.read(limit + 1)
    if len(data) > limit: raise ValueError("Source exceeds size limit")
    return data

def official_icon(package_name: str) -> tuple[bytes, str]:
    source = f"https://play.google.com/store/apps/details?id={package_name}&hl=en&gl=US"
    page = download(source, 4 * 1024 * 1024).decode("utf-8")
    match = re.search(r'<meta property="og:image" content="([^"]+)"', page)
    if not match: raise ValueError("No official icon")
    url = html.unescape(match.group(1))
    if not url.startswith("https://play-lh.googleusercontent.com/"):
        raise ValueError("Unexpected official image host")
    data = download(url.split("=")[0] + "=s192", MAX_ICON_BYTES)
    image_extension(data)
    return data, source

def apk_icons(roots: list[Path], wanted: set[str]):
    """Use APK-declared raster icons only; never guess an obfuscated resource."""
    from nikgapps_package_pipeline.apk import find_aapt2
    aapt2 = find_aapt2()
    for root in roots:
        for apk in sorted(root.rglob("*.apk")):
            if not wanted: return
            result = subprocess.run([aapt2, "dump", "badging", str(apk)],
                                    capture_output=True, timeout=45)
            text = result.stdout.decode("utf-8", errors="replace")
            match = re.search(r"^package: name='([^']+)'", text, re.M)
            if not match or match[1] not in wanted: continue
            paths = re.findall(r"^application-icon-[0-9]+:'([^']+)'", text, re.M)
            with zipfile.ZipFile(apk) as archive:
                for resource in reversed(paths):
                    if not resource.endswith((".png", ".webp", ".jpg")): continue
                    data = archive.read(resource)
                    if len(data) > MAX_ICON_BYTES: continue
                    image_extension(data)
                    wanted.remove(match[1])
                    yield match[1], data, f"apk:{apk.relative_to(root).as_posix()}!/{resource}"
                    break

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", default="85036487")
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--publish", action="store_true")
    parser.add_argument("--apk-root", type=Path, action="append", default=[])
    args = parser.parse_args()
    _load_default_env()
    client = GitLabClient("https://gitlab.com", os.environ["GITLAB_TOKEN"])
    catalog = json.loads(client.read_repository_file(args.project, "catalog.json"))
    previous = client.read_repository_file(args.project, "icons.json")
    old_icons = json.loads(previous)["icons"] if previous else {}
    packages = sorted({v["packageName"] for p in catalog["packages"] if not p.get("internal")
                       for v in p["versions"].values() if v.get("packageName")})
    assets = args.work / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    icons, missing = dict(old_icons), []
    def fetch(package):
        try:
            data, source = official_icon(package)
            return package, data, source
        except (urllib.error.URLError, ValueError, TimeoutError):
            return package, None, None
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        for package, data, source in pool.map(fetch, packages):
            if data is None:
                if package not in icons: missing.append(package)
                continue
            sha = hashlib.sha256(data).hexdigest()
            asset = assets / f"{package}.{image_extension(data)}"
            asset.write_bytes(data)
            url = (f"https://gitlab.com/api/v4/projects/{args.project}/packages/generic/"
                   f"app-icons/{sha}/{asset.name}")
            if args.publish and old_icons.get(package, {}).get("sha256") != sha:
                client.upload_generic(args.project, "app-icons", sha, asset,
                                      {"png": "image/png", "jpg": "image/jpeg", "webp": "image/webp"}[asset.suffix[1:]])
            icons[package] = {"url": url, "sha256": sha, "size": len(data), "source": source}
            print(f"Icon ready: {package}", flush=True)
    roots = args.apk_root or [Path(__file__).resolve().parents[2] / f"{v}_stable" for v in (17, 16)]
    for package, data, source in apk_icons(roots, set(missing)):
        sha = hashlib.sha256(data).hexdigest()
        asset = assets / f"{package}.{image_extension(data)}"
        asset.write_bytes(data)
        url = f"https://gitlab.com/api/v4/projects/{args.project}/packages/generic/app-icons/{sha}/{asset.name}"
        if args.publish and old_icons.get(package, {}).get("sha256") != sha:
            client.upload_generic(args.project, "app-icons", sha, asset,
                                  {"png": "image/png", "jpg": "image/jpeg", "webp": "image/webp"}[asset.suffix[1:]])
        icons[package] = {"url": url, "sha256": sha, "size": len(data), "source": source}
        missing.remove(package)
        print(f"APK icon ready: {package}", flush=True)
    manifest = {"schemaVersion": 1, "updatedAt": datetime.now(timezone.utc).isoformat(),
                "icons": dict(sorted(icons.items()))}
    metadata = args.work / "metadata"
    metadata.mkdir(parents=True, exist_ok=True)
    (metadata / "icons.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    (args.work / "missing.json").write_text(json.dumps(missing, indent=2), encoding="utf-8")
    print(f"Ready: {len(icons)}; standard fallback: {len(missing)}", flush=True)
    if args.publish:
        client.commit_directory(args.project, metadata, message="Publish official app icon manifest")
        print("Published icons.json", flush=True)

if __name__ == "__main__": main()
