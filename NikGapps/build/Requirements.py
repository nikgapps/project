"""Payload requirements shared by registry publication and ZIP assembly."""
from functools import lru_cache


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
    names = {overlay.apk_name for overlay in package.overlay_list}
    if float(android_version) >= 17 and package_title == 'WebViewGoogle':
        # This compiled overlay is maintained in overlays_17 outside Library.py.
        names.add('WebViewGoogleOverlay.apk')
    return frozenset(names)
