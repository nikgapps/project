from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "niklibrary"))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "nikassets"))

try:
    from NikGapps.overlay_control import build_local_overlays
except ModuleNotFoundError:
    build_local_overlays = None


class FakeOverlay:
    folder = "ExampleOverlay"

    def build_apk_source(self, source: str) -> None:
        folder = Path(source) / self.folder
        folder.mkdir(parents=True)
        (folder / "apktool.yml").write_text("version: 2.9.0\n", encoding="utf-8")


@unittest.skipIf(build_local_overlays is None, "optional NikGapps build dependencies unavailable")
class OverlayControlTests(unittest.TestCase):
    def test_android_17_local_overlay_output(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)

            def fake_build(_self, folder_name: str) -> str:
                apk = Path(folder_name) / "dist" / "ExampleOverlay.apk"
                apk.parent.mkdir()
                apk.write_bytes(b"android-17-overlay")
                return str(apk)

            with patch(
                "NikGapps.overlay_control.NikGappsOverlays.get_overlay",
                return_value=[FakeOverlay()],
            ), patch("NikGapps.overlay_control.Cmd.build_overlay", new=fake_build):
                built = build_local_overlays(
                    "17", root / "overlays_17_source", root / "overlays_17"
                )
            self.assertEqual(len(built), 1)
            self.assertEqual(Path(built[0]).read_bytes(), b"android-17-overlay")


if __name__ == "__main__":
    unittest.main()
