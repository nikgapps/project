from pathlib import Path
import tarfile
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from NikGapps.build.Build import Build
from NikGapps.helper import Config
from NikGapps.helper.AppSet import AppSet
from NikGapps.helper.Package import Package
from NikGapps.helper.compression.CompOps import CompOps
from niklibrary.compression.Modes import Modes
from niklibrary.helper.Statics import Statics


class ReadonlyPackageSourceTests(unittest.TestCase):
    def test_build_normalizes_archive_text_without_touching_sources(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source" / "Example" / "Example" / "___etc___sysconfig"
            source.mkdir(parents=True)
            original = {
                "lf.xml": b"<config />\n",
                "crlf.xml": '<config name="caf\u00e9" />\r\n'.encode("utf-8") + b"\r\n" * 504,
                "settings.prop": b"example.enabled=true\r\n",
                "binary.bin": b"\x00\xff\r\n\x01",
            }
            for name, content in original.items():
                (source / name).write_bytes(content)
            before = {name: (source / name).stat().st_mtime_ns for name in original}
            package = Package("Example", "example.payload", package_title="Example", partition="product")
            with patch.object(Config, "APK_SOURCE", str(root / "source")), patch.object(Config, "OVERLAY_SOURCE", str(root / "overlays")), patch.object(Config, "PACKAGE_SOURCE", "local"):
                built = Build.build_from_directory([AppSet("Example", [package])], "17")[0].package_list[0]

            for mode, suffix in [(Modes.ZIP, ".zip"), (Modes.TAR_XZ, ".tar.xz")]:
                destination = root / ("package" + suffix)
                self.assertTrue(CompOps.compress_package(str(destination), built, mode))
                self.assertEqual(built.pkg_size, sum(Statics.get_file_bytes(source / name) for name in original))
                if mode == Modes.ZIP:
                    with zipfile.ZipFile(destination) as archive:
                        actual = {name: archive.read("___etc___sysconfig/" + name) for name in original}
                else:
                    with tarfile.open(destination) as archive:
                        actual = {name: archive.extractfile("___etc___sysconfig/" + name).read() for name in original}
                for name, content in original.items():
                    with self.subTest(format=mode, name=name):
                        expected = content.replace(b"\r\n", b"\n") if name.endswith((".xml", ".prop")) else content
                        self.assertEqual(actual[name], expected)
                        self.assertEqual((source / name).read_bytes(), content)
                        self.assertEqual((source / name).stat().st_mtime_ns, before[name])


if __name__ == "__main__":
    unittest.main()
