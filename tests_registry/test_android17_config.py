import unittest

from NikGapps.config.NikGappsConfig import NikGappsConfig


class Android17ConfigTests(unittest.TestCase):
    def test_removed_packages_are_absent_only_from_android_17(self):
        removed = (
            "Books=", ">>GoogleContactsSyncAdapter=",
            ">>GoogleCalendarSyncAdapter=", ">>GoogleOneTimeInitializer=",
        )
        current = NikGappsConfig("17").get_nikgapps_config()
        previous = NikGappsConfig("16").get_nikgapps_config()
        self.assertIn("Version=40", current)
        for entry in removed:
            with self.subTest(entry=entry):
                self.assertNotIn(entry, current)
                self.assertIn(entry, previous)


if __name__ == "__main__":
    unittest.main()
