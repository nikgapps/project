import unittest

from NikGapps.build.PackageConstants import PackageConstants


class PixelSetupScriptTests(unittest.TestCase):
    def test_pixel_alias_selects_expressive_profile_with_legacy_fallback(self):
        script = PackageConstants.get_package_script("SetupWizardPixel")
        self.assertIsNotNone(script)
        self.assertIn('if [ "$androidVersion" -ge 17 ]; then', script)
        modern, legacy = script.split('       else\n', 1)
        self.assertIn('"setupwizard.theme" "glif_expressive"', modern)
        self.assertIn('"ro.setupwizard.mode" "OPTIONAL"', modern)
        self.assertIn('"setupwizard.feature.baseline_setupwizard_enabled" "true"', modern)
        self.assertIn(PackageConstants.get_package_script("SetupWizard"), legacy)

    def test_optional_companion_and_warranty_are_not_forced_on(self):
        modern = PackageConstants.get_package_script("SetupWizardPixel").split('       else\n', 1)[0]
        for property_name in ["enable_setup_companion", "show_digital_warranty"]:
            self.assertIn(f'"setupwizard.feature.{property_name}" "false"', modern)
        self.assertNotIn("ro.setupwizard.esim_cid_ignore", modern)

    def test_partner_does_not_reset_base_wizard_properties(self):
        self.assertIsNone(PackageConstants.get_package_script("PixelSetupWizard"))
        self.assertIn('"setupwizard.theme" "glif_v3_light"', PackageConstants.get_package_script("SetupWizard"))


if __name__ == "__main__":
    unittest.main()
