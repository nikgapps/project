from __future__ import annotations

import re
import subprocess
import os
from pathlib import Path

from .errors import PipelineError
from .models import ApkMetadata


class ApkInspector:
    """APK metadata boundary; injectable for tests and alternate tooling."""

    def inspect(self, apk: Path) -> ApkMetadata:
        raise NotImplementedError

    def privileged_permissions(self, apk: Path) -> list[str]:
        """Return permissions requested/declared by a privileged APK."""
        return []


class Aapt2Inspector(ApkInspector):
    def __init__(self, executable: str = "aapt2") -> None:
        self.executable = executable

    def inspect(self, apk: Path) -> ApkMetadata:
        badging = self._dump(["dump", "badging", str(apk)], apk)
        if not re.search(r"^sdkVersion:'\d+'", badging, re.MULTILINE):
            manifest = self._dump(
                ["dump", "xmltree", str(apk), "--file", "AndroidManifest.xml"],
                apk,
            )
            uses_sdk = re.search(
                r"E: uses-sdk\b(?P<body>.*?)(?=\n\s*E: |\Z)",
                manifest,
                re.DOTALL,
            )
            minimum = re.search(
                r"minSdkVersion[^=]*=(?:\(type [^)]+\))?(\d+)",
                uses_sdk.group("body") if uses_sdk else "",
            )
            if not minimum:
                raise PipelineError(
                    f"Missing minimum SDK in both badging and manifest output for {apk}"
                )
            badging += f"\nsdkVersion:'{minimum.group(1)}'\n"
        return self.parse(badging, apk)

    def privileged_permissions(self, apk: Path) -> list[str]:
        output = self._dump(["dump", "permissions", str(apk)], apk)
        permissions: set[str] = set()
        for line in output.splitlines():
            stripped = line.strip()
            requested = re.match(r"uses-permission(?:-sdk-\d+)?:\s+name='([^']+)'", stripped)
            declared = re.match(r"permission:\s+(?:name=)?'?([^'\s]+)'?", stripped)
            match = requested or declared
            if match:
                permissions.add(match.group(1))
        return sorted(permissions)

    def _dump(self, arguments: list[str], apk: Path) -> str:
        try:
            result = subprocess.run(
                [self.executable, *arguments],
                check=True,
                capture_output=True,
            )
        except FileNotFoundError as exc:
            raise PipelineError(
                f"{self.executable!r} was not found. Install Android build-tools "
                "or pass --aapt2 with its full path."
            ) from exc
        except subprocess.CalledProcessError as exc:
            raw_detail = exc.stderr or exc.stdout or b""
            detail = raw_detail.decode("utf-8", errors="replace").strip()
            raise PipelineError(f"aapt2 failed for {apk}: {detail}") from exc
        return result.stdout.decode("utf-8", errors="replace")

    @staticmethod
    def parse(text: str, apk: Path | None = None) -> ApkMetadata:
        def required(pattern: str, name: str) -> str:
            match = re.search(pattern, text, re.MULTILINE)
            if not match:
                raise PipelineError(f"Missing {name} in aapt2 output for {apk or 'APK'}")
            return match.group(1)

        return ApkMetadata(
            package_name=required(r"^package: name='([^']+)'", "package name"),
            version_name=required(r"^package:.*versionName='([^']+)'", "version name"),
            version_code=int(required(r"^package:.*versionCode='(\d+)'", "version code")),
            min_api=int(required(r"^sdkVersion:'(\d+)'", "minimum SDK")),
            target_api=int(required(r"^targetSdkVersion:'(\d+)'", "target SDK")),
        )


def find_aapt2() -> str:
    """Find aapt2 in PATH or a conventional local Android SDK."""
    import shutil

    on_path = shutil.which("aapt2")
    if on_path:
        return on_path
    project_root = Path(__file__).resolve().parent.parent
    bundled = (
        project_root.parent / "nikassets" / "nikassets" / "helper" / "assets"
        / "bin" / ("Windows" if os.name == "nt" else "Linux")
        / ("aapt2.exe" if os.name == "nt" else "aapt2")
    )
    if bundled.is_file():
        return str(bundled)
    sdk_roots = [
        os.environ.get("ANDROID_SDK_ROOT"),
        os.environ.get("ANDROID_HOME"),
        str(Path.home() / "AppData" / "Local" / "Android" / "Sdk"),
    ]
    for raw_root in sdk_roots:
        if not raw_root:
            continue
        build_tools = Path(raw_root) / "build-tools"
        try:
            exists = build_tools.is_dir()
        except OSError:
            continue
        if not exists:
            continue
        try:
            candidates = sorted(
                build_tools.glob("*/aapt2.exe" if os.name == "nt" else "*/aapt2"),
                reverse=True,
            )
        except OSError:
            continue
        if candidates:
            return str(candidates[0])
    return "aapt2"
