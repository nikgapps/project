from __future__ import annotations

import argparse
import json
import logging
import os
import shutil
import sys
import urllib.parse
from pathlib import Path
from typing import Sequence

from .apk import Aapt2Inspector, find_aapt2
from .config import load_config, platform_api_for_android
from .compat import LegacyCompatibilityExporter
from .errors import PipelineError
from .gitlab import GitLabClient
from .pipeline import MigrationPipeline
from .scanner import LegacyRepositoryScanner
from .upgrade import StableTreeUpgrader

LOG = logging.getLogger("nikgapps.package_pipeline")
DEFAULT_INPUT = Path(r"D:\workspace\python\16_stable")
DEFAULT_OUTPUT = Path(r"D:\workspace\python\16_STABLE_PREBUILT_RELEASE")
DEFAULT_CONFIG = Path(__file__).with_name("nikgapps-pipeline.example.json")
DEFAULT_GITLAB_PROJECT = "85036487"


def _load_env_file(path: Path) -> bool:
    """Load simple KEY=VALUE entries without overriding the process environment."""
    if not path.is_file():
        return False
    try:
        lines = path.read_text(encoding="utf-8-sig").splitlines()
    except OSError as exc:
        raise PipelineError(f"Cannot read environment file {path}: {exc}") from exc
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.removeprefix("export ").split("=", 1)
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        if key:
            os.environ.setdefault(key, value)
    return True


def _load_default_env() -> None:
    project_root = Path(__file__).resolve().parent.parent
    candidates = [
        Path.cwd() / ".env",
        Path.cwd() / "NikGapps" / ".env",
        project_root / "NikGapps" / ".env",
    ]
    seen: set[Path] = set()
    for candidate in candidates:
        resolved = candidate.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        if _load_env_file(resolved):
            LOG.debug("Loaded environment values from %s", resolved)


def _common_gitlab(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--gitlab-url", default="https://gitlab.com")
    parser.add_argument(
        "--token-env",
        default="GITLAB_TOKEN",
        help="environment variable containing a GitLab API token",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="nikgapps-package-pipeline",
        description="Migrate legacy NikGapps packages and publish immutable artifacts.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    commands = parser.add_subparsers(dest="command", required=True)

    migrate = commands.add_parser("migrate", help="scan, validate, ZIP, and catalog packages")
    migrate.add_argument("--verbose", action="store_true")
    migrate.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    migrate.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    migrate.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    migrate.add_argument("--android-version", default="16")
    migrate.add_argument(
        "--platform-api", type=int,
        help="override platform API; otherwise derived from --android-version",
    )
    migrate.add_argument("--channel", default="stable")
    migrate.add_argument("--aapt2", default=find_aapt2())
    migrate.add_argument(
        "--package",
        action="append",
        help="migrate only this package name or AppSet/Package; repeat as needed",
    )
    migrate.add_argument(
        "--artifact-base-url",
        help="registry URL through .../packages/generic; derived when --gitlab-project is given",
    )
    migrate.add_argument(
        "--gitlab-project", default=DEFAULT_GITLAB_PROJECT,
        help="numeric ID or URL-encoded project path",
    )
    migrate.add_argument("--publish", action="store_true")
    migrate.add_argument(
        "--fresh-metadata", action="store_true",
        help="discard local/remote catalog history and generate metadata only from this run",
    )
    migrate.add_argument(
        "--metadata-branch",
        default="main",
        help="branch receiving generated metadata when publishing",
    )
    migrate.add_argument(
        "--create-project",
        action="store_true",
        help="create the configured catalog project before publishing",
    )
    migrate.add_argument("--namespace-id", type=int)
    migrate.add_argument(
        "--namespace",
        default="nikgapps",
        help="GitLab namespace path used when creating the project",
    )
    migrate.add_argument("--visibility", choices=["public", "private", "internal"], default="public")
    migrate.add_argument("--compact", action="store_true")
    migrate.add_argument(
        "--compat-output",
        type=Path,
        help="optionally materialize the legacy AppSet/Package/___path tree",
    )
    _common_gitlab(migrate)

    create = commands.add_parser("create-project", help="create a GitLab catalog project")
    create.add_argument("--verbose", action="store_true")
    create.add_argument("--name", default="nikgapps-package-catalog")
    create.add_argument("--namespace-id", type=int)
    create.add_argument(
        "--namespace",
        default="nikgapps",
        help="GitLab namespace path",
    )
    create.add_argument("--visibility", choices=["public", "private", "internal"], default="public")
    _common_gitlab(create)

    reset = commands.add_parser(
        "reset-registry",
        help="list or delete all Generic Package Registry packages in the configured project",
    )
    reset.add_argument("--verbose", action="store_true")
    reset.add_argument("--gitlab-project", default=DEFAULT_GITLAB_PROJECT)
    reset.add_argument(
        "--confirm-project",
        help="perform deletion only when this exactly matches --gitlab-project; otherwise dry-run",
    )
    _common_gitlab(reset)

    upgrade = commands.add_parser(
        "upgrade", help="create a stable legacy tree from a newer Mustang image"
    )
    upgrade.add_argument("--template", type=Path, required=True)
    upgrade.add_argument("--baseline-firmware", type=Path, required=True)
    upgrade.add_argument("--target-firmware", type=Path, required=True)
    upgrade.add_argument("--output", type=Path, required=True)
    return parser


def _client(args: argparse.Namespace) -> GitLabClient:
    _load_default_env()
    token = os.environ.get(args.token_env)
    if not token:
        raise PipelineError(
            f"GitLab token environment variable {args.token_env!r} is not set"
        )
    return GitLabClient(args.gitlab_url, token)


def _migrate(args: argparse.Namespace) -> int:
    derived_platform_api = (
        args.platform_api
        if args.platform_api is not None
        else platform_api_for_android(args.android_version)
    )
    config = load_config(
        args.config,
        android_version=args.android_version,
        platform_api=derived_platform_api,
        channel=args.channel,
    )
    client: GitLabClient | None = None
    project = args.gitlab_project
    if args.create_project:
        client = _client(args)
        if args.namespace_id is not None:
            created = client.create_project(
                config.repository_name,
                namespace_id=args.namespace_id,
                visibility=args.visibility,
            )
        else:
            created = client.create_project_in_namespace(
                config.repository_name,
                args.namespace,
                visibility=args.visibility,
            )
        project = str(created.id)
        LOG.info("Created GitLab project %s (%s)", created.path_with_namespace, created.web_url)
    if args.publish and not project:
        raise PipelineError("--publish requires --gitlab-project or --create-project")
    if args.publish and client is None:
        client = _client(args)
    metadata_directory = args.output / "metadata"
    if args.fresh_metadata:
        if not args.publish:
            raise PipelineError("--fresh-metadata requires --publish")
        if metadata_directory.exists():
            resolved_metadata = metadata_directory.resolve()
            resolved_output = args.output.resolve()
            if resolved_metadata.parent != resolved_output:
                raise PipelineError(f"Refusing to clear unexpected metadata path: {resolved_metadata}")
            shutil.rmtree(resolved_metadata)
            LOG.info("Cleared local metadata history for a fresh catalog")
    if args.publish and not args.fresh_metadata:
        assert client is not None and project is not None
        metadata = args.output / "metadata"
        release_path = (
            f"releases/android-{config.android_version}-{config.architecture}.json"
        )
        for relative in ("catalog.json", "appsets.json", release_path):
            local = metadata / Path(relative)
            if local.exists():
                continue
            remote = client.read_repository_file(
                project, relative, branch=args.metadata_branch
            )
            if remote is not None:
                local.parent.mkdir(parents=True, exist_ok=True)
                local.write_bytes(remote)
                LOG.info("Seeded existing metadata from %s", relative)
    base_url = args.artifact_base_url
    if not base_url:
        if project:
            encoded_project = urllib.parse.quote(str(project), safe="")
            base_url = (
                f"{args.gitlab_url.rstrip('/')}/api/v4/projects/"
                f"{encoded_project}/packages/generic"
            )
        else:
            base_url = "https://example.invalid/api/v4/projects/PROJECT/packages/generic"
            LOG.info("Local preview mode; catalog artifact URLs are placeholders")
    pipeline = MigrationPipeline(LegacyRepositoryScanner(), Aapt2Inspector(args.aapt2))
    packages = pipeline.migrate(
        args.input,
        args.output,
        config,
        artifact_base_url=base_url,
        pretty=not args.compact,
        package_filter=set(args.package) if args.package else None,
    )
    if args.compat_output:
        LegacyCompatibilityExporter().export(packages, args.compat_output)
        LOG.info("Materialized legacy builder input at %s", args.compat_output)
    if args.publish:
        assert client is not None and project is not None
        urls = pipeline.publish(packages, client, project)
        (args.output / "published-urls.json").write_text(
            json.dumps(urls, indent=2) + "\n",
            encoding="utf-8",
        )
        client.commit_directory(
            project,
            args.output / "metadata",
            branch=args.metadata_branch,
        )
        LOG.info("Committed generated metadata to %s branch %s", project, args.metadata_branch)
    LOG.info("Completed %d unique packages", len(packages))
    return 0


def _reset_registry(args: argparse.Namespace) -> int:
    client = _client(args)
    packages = client.list_packages(args.gitlab_project, package_type="generic")
    if not packages:
        print(f"GitLab project {args.gitlab_project} has no Generic Registry packages.")
        return 0
    total = len(packages)
    print(f"Generic packages in GitLab project {args.gitlab_project}: {total}")
    for package in packages:
        print(f"- [{package.id}] {package.name} {package.version}")
    if args.confirm_project != str(args.gitlab_project):
        print("Dry run only; nothing was deleted.")
        print(
            "To permanently delete every package listed above, rerun with "
            f"--confirm-project {args.gitlab_project}"
        )
        return 0
    print(f"Deleting {total} Generic Registry packages...")
    for index, package in enumerate(packages, 1):
        client.delete_package(args.gitlab_project, package.id)
        print(f"[{index}/{total}] Deleted {package.name} {package.version}")
    print("Package Registry reset completed. This deletion is permanent.")
    print("Now run: migrate --publish --fresh-metadata --verbose")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if getattr(args, "verbose", False) else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    try:
        if args.command == "create-project":
            client = _client(args)
            if args.namespace_id is not None:
                project = client.create_project(
                    args.name,
                    namespace_id=args.namespace_id,
                    visibility=args.visibility,
                )
            else:
                project = client.create_project_in_namespace(
                    args.name,
                    args.namespace,
                    visibility=args.visibility,
                )
            print(json.dumps(project.__dict__, indent=2))
            return 0
        if args.command == "reset-registry":
            return _reset_registry(args)
        if args.command == "upgrade":
            report = StableTreeUpgrader().upgrade(
                args.template, args.baseline_firmware, args.target_firmware, args.output
            )
            print(json.dumps(report.as_dict(), indent=2))
            return 0
        return _migrate(args)
    except PipelineError as exc:
        LOG.error("%s", exc)
        return 2


if __name__ == "__main__":
    sys.exit(main())
