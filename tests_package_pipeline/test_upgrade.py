from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from nikgapps_package_pipeline.errors import PipelineError
from nikgapps_package_pipeline.upgrade import StableTreeUpgrader


class StableTreeUpgradeTests(unittest.TestCase):
    @staticmethod
    def inventory(root: Path, package: str, location: str, *, stub: bool = False) -> None:
        root.mkdir(parents=True, exist_ok=True)
        (root / "mustang.json").write_text(json.dumps({package: [{
            "location": location,
            "type": Path(location).parts[-3],
            "isstub": stub,
        }]}), encoding="utf-8")

    def test_upgrade_uses_package_identity_and_copies_new_dependencies(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            template = root / "16_stable"
            old = root / "16_mustang"
            new = root / "17_mustang"
            output = root / "17_stable"
            old_location = "product/priv-app/AppOld/AppOld.apk"
            new_location = "product/priv-app/AppNew_17/AppNew_17.apk"
            self.inventory(old, "com.example", old_location)
            self.inventory(new, "com.example", new_location)
            (old / old_location).parent.mkdir(parents=True)
            (old / old_location).write_bytes(b"old")
            (new / new_location).parent.mkdir(parents=True)
            (new / new_location).write_bytes(b"new")
            (new / new_location).with_suffix(".apk.prof").write_bytes(b"profile")
            template_apk = template / "Set" / "App" / "___priv-app___AppOld" / "AppOld.apk"
            template_apk.parent.mkdir(parents=True)
            template_apk.write_bytes(b"template")

            report = StableTreeUpgrader().upgrade(template, old, new, output)

            upgraded = output / "Set" / "App" / "___priv-app___AppNew_17"
            self.assertEqual((upgraded / "AppNew_17.apk").read_bytes(), b"new")
            self.assertEqual((upgraded / "AppNew_17.apk.prof").read_bytes(), b"profile")
            self.assertEqual(report.upgraded_packages, ["Set/App"])
            self.assertFalse((output / "Set" / "App" / "___priv-app___AppOld").exists())

    def test_refuses_to_mix_payload_into_existing_output(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for name in ("template", "old", "new", "output"):
                (root / name).mkdir()
            self.inventory(root / "old", "com.example", "product/app/A/A.apk")
            self.inventory(root / "new", "com.example", "product/app/A/A.apk")
            with self.assertRaises(PipelineError):
                StableTreeUpgrader().upgrade(
                    root / "template", root / "old", root / "new", root / "output"
                )


if __name__ == "__main__":
    unittest.main()
