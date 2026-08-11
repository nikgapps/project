import tempfile
import unittest
from pathlib import Path

import yaml

from NikGapps.helper.overlay.ApkMetaInfo import ApkMetaInfo
from niklibrary.helper.Statics import Statics


class ApkMetaInfoTests(unittest.TestCase):
    def setUp(self):
        self.original_android_17 = Statics.android_versions.get("17")
        Statics.android_versions["17"] = {"sdk": "37", "code": "CinnamonBun"}

    def tearDown(self):
        if self.original_android_17 is None:
            Statics.android_versions.pop("17", None)
        else:
            Statics.android_versions["17"] = self.original_android_17

    def test_apktool_3_metadata_uses_numeric_sdk_fields(self):
        metadata = ApkMetaInfo("ExampleOverlay.apk", "17").to_dict()

        self.assertEqual(37, metadata["sdkInfo"]["minSdkVersion"])
        self.assertEqual(37, metadata["sdkInfo"]["targetSdkVersion"])
        self.assertEqual(37, metadata["versionInfo"]["versionCode"])
        self.assertEqual(
            {"packageId": 127, "renameManifestPackage": None},
            metadata["resourcesInfo"],
        )
        self.assertNotIn("packageInfo", metadata)

    def test_written_metadata_round_trips_numbers_as_numbers(self):
        with tempfile.TemporaryDirectory() as directory:
            ApkMetaInfo("ExampleOverlay.apk", "17").write(directory, "apktool.yml")
            metadata = yaml.safe_load(
                Path(directory, "apktool.yml").read_text(encoding="utf-8")
            )

        self.assertIsInstance(metadata["sdkInfo"]["minSdkVersion"], int)
        self.assertIsInstance(metadata["versionInfo"]["versionCode"], int)


if __name__ == "__main__":
    unittest.main()
