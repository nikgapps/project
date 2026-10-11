import unittest
from unittest.mock import patch

from NikGapps.build.NikGappsManager import NikGappsManager


class VersionScopedPackageTests(unittest.TestCase):
    @staticmethod
    def package_names(appsets):
        return {package.package_title for appset in appsets for package in appset.package_list}

    @patch.object(NikGappsManager, "get_package_overlays", return_value=[])
    def test_sync_adapters_are_excluded_only_from_android_17(self, _overlays):
        adapters = {"GoogleContactsSyncAdapter", "GoogleCalendarSyncAdapter"}
        for version in ("15", "16", "17", "18"):
            manager = NikGappsManager(version)
            for selection in (manager.get_core_package, manager.get_go_package):
                with self.subTest(version=version, selection=selection.__name__):
                    names = self.package_names(selection())
                    if version == "17":
                        self.assertFalse(adapters & names)
                    else:
                        self.assertTrue(adapters <= names)

    @patch.object(NikGappsManager, "get_package_overlays", return_value=[])
    def test_standard_and_pixel_initializer_are_excluded_only_from_android_17(self, _overlays):
        for version in ("15", "16", "17", "18"):
            manager = NikGappsManager(version)
            standard = self.package_names(manager.get_omni_package())
            pixel = self.package_names(manager.get_addon_packages(addon_name="PixelSetupWizard"))
            with self.subTest(version=version):
                self.assertEqual("GoogleOneTimeInitializer" in standard, version != "17")
                self.assertEqual("GoogleOneTimeInitializerPixel" in pixel, version != "17")


if __name__ == "__main__":
    unittest.main()
