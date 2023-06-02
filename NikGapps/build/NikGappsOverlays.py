from NikGapps.build.NikGappsPackages import NikGappsPackages
from NikGapps.helper.overlay.Overlay import Overlay


class NikGappsOverlays:

    @staticmethod
    def get_overlay(android_version):
        overlay_list = []
        for packages in NikGappsPackages.get_packages("all", android_version=android_version):
            for pkg in packages.package_list:
                for overlay in pkg.overlay_list:
                    overlay: Overlay
                    overlay_list.append(overlay)
        return overlay_list
