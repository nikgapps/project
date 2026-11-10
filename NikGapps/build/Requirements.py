"""Payload requirements shared by registry publication and ZIP assembly."""
from functools import lru_cache
import zipfile


def validate_overlay(apk):
    try:
        with zipfile.ZipFile(apk) as archive:
            if 'AndroidManifest.xml' not in archive.namelist() or archive.testzip():
                raise ValueError('Missing or corrupt AndroidManifest.xml')
    except (OSError, zipfile.BadZipFile, ValueError) as error:
        raise ValueError(f'Invalid compiled overlay APK: {apk}: {error}') from error


@lru_cache(maxsize=None)
def required_overlays(package_title, android_version):
    if float(android_version) <= 12:
        return frozenset()
    from NikGapps.overlay_control import register_android_platform
    from NikGapps.build.NikGappsManager import NikGappsManager
    register_android_platform(str(android_version))
    try:
        package = NikGappsManager(str(android_version)).create_package(package_title)
    except ValueError:  # Generic pipeline fixtures/custom packages have no NikGapps definition.
        return frozenset()
    return frozenset(overlay.apk_name for overlay in package.overlay_list)
