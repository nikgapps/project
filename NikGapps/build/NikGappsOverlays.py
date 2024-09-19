from NikGapps.config.NikGappsConfig import NikGappsConfig
from NikGapps.helper.overlay.Overlay import Overlay


class NikGappsOverlays:

    @staticmethod
    def get_overlay(android_version):
        overlay_list = []
        config_obj = NikGappsConfig(android_version=android_version)
        for packages in config_obj.package_manager.get_packages("all"):
            for pkg in packages.package_list:
                for overlay in pkg.overlay_list:
                    overlay: Overlay
                    overlay_list.append(overlay)
        return overlay_list
