from __future__ import annotations

import argparse
import logging
import os
from pathlib import Path
from typing import Sequence

from nikgapps_package_pipeline.apk import find_aapt2
from nikgapps_package_pipeline.cli import _load_default_env
from nikgapps_package_pipeline.errors import PipelineError
from nikgapps_package_pipeline.gitlab import GitLabClient

from .service import RegistryService, SyncRequest

DEFAULT_CONFIG = Path(__file__).resolve().parent.parent / "nikgapps_package_pipeline" / "nikgapps-pipeline.example.json"
DEFAULT_BUSYBOX = Path(__file__).resolve().parent.parent / ".venv" / "Lib" / "site-packages" / "nikassets" / "helper" / "assets" / "busybox"
DEFAULT_BUILDER_ASSETS = Path(__file__).resolve().parent.parent / "NikGapps" / "helper" / "assets"
DEFAULT_RELEASE_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MULTI_RELEASE_WORK = DEFAULT_RELEASE_ROOT / "MULTI_RELEASE_PREVIEW"


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(
        prog="nikgapps-registry",
        description="Publish legacy NikGapps packages and metadata to GitLab.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    root.add_argument("--gitlab-url", default="https://gitlab.com")
    root.add_argument("--token-env", default="GITLAB_TOKEN")
    root.add_argument("--verbose", action="store_true")
    commands = root.add_subparsers(dest="command", required=True)

    sync = commands.add_parser("sync", help="ZIP, upload, and catalog legacy packages")
    sync.add_argument("--source", type=Path,
                      help="defaults to VERSION_stable beside the project directory")
    sync.add_argument("--work", type=Path, default=DEFAULT_MULTI_RELEASE_WORK)
    sync.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    sync.add_argument("--project", required=True, help="GitLab project ID or encoded path")
    sync.add_argument("--android-version", required=True)
    sync.add_argument("--platform-api", type=int)
    sync.add_argument("--arch", default="arm64-v8a")
    sync.add_argument("--channel", default="stable")
    sync.add_argument("--metadata-branch", default="main")
    sync.add_argument("--aapt2", default=find_aapt2())
    sync.add_argument(
        "--overlays", type=Path,
        help="compiled overlay repository containing <PackageName>Overlay/*.apk",
    )
    sync.add_argument("--busybox", type=Path, default=DEFAULT_BUSYBOX)
    sync.add_argument("--builder-assets", type=Path, default=DEFAULT_BUILDER_ASSETS)
    sync.add_argument("--package", action="append", default=[])
    sync.add_argument("--fresh", action="store_true", help="ignore existing catalog history")
    sync.add_argument("--compact", action="store_true")
    sync.add_argument("--verbose", action="store_true")

    reset = commands.add_parser("reset", help="delete Generic Registry packages")
    reset.add_argument("--project", required=True)
    reset.add_argument("--confirm-project", help="exact project value required for deletion")

    reset_sync = commands.add_parser(
        "reset-and-sync", help="reset once, then publish one or more Android releases"
    )
    reset_sync.add_argument("--confirm-project", required=True,
                            help="GitLab project ID; exact confirmation required for deletion")
    reset_sync.add_argument("--project", help="target project; defaults to --confirm-project")
    reset_sync.add_argument("--android-version", required=True,
                            help="one version or comma-separated versions, for example 17 or 16,17")
    reset_sync.add_argument("--work", type=Path, default=DEFAULT_MULTI_RELEASE_WORK)
    reset_sync.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    reset_sync.add_argument("--platform-api", type=int)
    reset_sync.add_argument("--arch", default="arm64-v8a")
    reset_sync.add_argument("--channel", default="stable")
    reset_sync.add_argument("--metadata-branch", default="main")
    reset_sync.add_argument("--aapt2", default=find_aapt2())
    reset_sync.add_argument("--busybox", type=Path, default=DEFAULT_BUSYBOX)
    reset_sync.add_argument("--builder-assets", type=Path, default=DEFAULT_BUILDER_ASSETS)
    reset_sync.add_argument("--package", action="append", default=[])
    reset_sync.add_argument("--compact", action="store_true")
    reset_sync.add_argument("--verbose", action="store_true")
    return root


def _service(args: argparse.Namespace) -> RegistryService:
    _load_default_env()
    token = os.environ.get(args.token_env)
    if not token:
        raise PipelineError(f"GitLab token variable {args.token_env!r} is not set")
    return RegistryService(GitLabClient(args.gitlab_url, token), aapt2=getattr(args, "aapt2", "aapt2"))


def main(argv: Sequence[str] | None = None) -> int:
    args = parser().parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)
    try:
        service = _service(args)
        if args.command == "reset":
            packages = service.registry_packages(args.project)
            for package in packages:
                print(f"- [{package.id}] {package.name} {package.version}")
            if args.confirm_project != args.project:
                print(f"Dry run. Add --confirm-project {args.project} to delete {len(packages)} package(s).")
                return 0
            deleted = service.reset(args.project)
            print(f"Deleted {len(deleted)} Generic Registry package(s).")
            print("Run sync --fresh next to replace catalog and AppSet metadata.")
            return 0
        if args.command == "reset-and-sync":
            project = args.project or args.confirm_project
            if args.confirm_project != project:
                raise PipelineError("--confirm-project must exactly match --project")
            versions = [value.strip() for value in args.android_version.split(",") if value.strip()]
            if not versions:
                raise PipelineError("--android-version must contain at least one version")
            releases = [
                (version, DEFAULT_RELEASE_ROOT / f"{version}_stable",
                 DEFAULT_RELEASE_ROOT / f"overlays_{version}")
                for version in versions
            ]
            for version, source, overlays in releases:
                if not source.is_dir():
                    raise PipelineError(f"Android {version} source directory does not exist: {source}")
                if not overlays.is_dir():
                    raise PipelineError(f"Android {version} overlay directory does not exist: {overlays}")
            full_reset = len(releases) > 1
            if full_reset:
                deleted = service.reset(project)
                print(f"Deleted {len(deleted)} Generic Registry package(s).")
            else:
                print(
                    f"Android {versions[0]} selected: preserving all other registry packages "
                    "and metadata; performing a version-scoped incremental rebuild."
                )
            total_urls = 0
            for index, (version, source, overlays) in enumerate(releases):
                print(f"[{index + 1}/{len(releases)}] Syncing Android {version}")
                urls = service.sync(SyncRequest(
                    source=source, work=args.work, config=args.config,
                    project=project, android_version=version,
                    architecture=args.arch, channel=args.channel,
                    platform_api=args.platform_api, metadata_branch=args.metadata_branch,
                    package_filter=frozenset(args.package), fresh=full_reset and index == 0,
                    pretty=not args.compact, overlays=overlays,
                    busybox=args.busybox, builder_assets=args.builder_assets,
                ))
                total_urls += len(urls)
            print(f"Published {total_urls} ZIP package(s) across Android {', '.join(versions)}.")
            return 0
        source = args.source or DEFAULT_RELEASE_ROOT / f"{args.android_version}_stable"
        overlays = args.overlays
        if overlays is None:
            discovered_overlays = DEFAULT_RELEASE_ROOT / f"overlays_{args.android_version}"
            overlays = discovered_overlays if discovered_overlays.is_dir() else None
        urls = service.sync(SyncRequest(
            source=source, work=args.work, config=args.config,
            project=args.project, android_version=args.android_version,
            architecture=args.arch, channel=args.channel,
            platform_api=args.platform_api, metadata_branch=args.metadata_branch,
            package_filter=frozenset(args.package), fresh=args.fresh,
            pretty=not args.compact,
            overlays=overlays,
            busybox=args.busybox,
            builder_assets=args.builder_assets,
        ))
        print(f"Published {len(urls)} ZIP package(s) and updated metadata.")
        return 0
    except PipelineError as exc:
        logging.error("%s", exc)
        return 2
