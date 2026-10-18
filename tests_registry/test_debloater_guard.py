"""Installer validation tests: shell removal is faked, never run against a device."""
import pathlib
import os
import shutil
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
GUARD = ROOT / "NikGapps/helper/assets/debloater_guard.sh"
GIT_BASH = pathlib.Path(r"C:\Program Files\Git\bin\bash.exe")
BASH = str(GIT_BASH) if GIT_BASH.exists() else shutil.which("bash")


class DebloaterGuardTests(unittest.TestCase):
    def test_android_and_python_share_identical_installer_policy(self):
        android = ROOT.parents[1] / "android/NikGapps/app/src/main/res/raw/debloater_guard.sh"
        if not android.exists():
            self.skipTest("Android checkout is not present in this CI job")
        self.assertEqual(GUARD.read_text(), android.read_text())

    @unittest.skipUnless(BASH, "POSIX shell is unavailable")
    def test_syntax_and_target_policy(self):
        subprocess.run([BASH, "-n", str(GUARD)], check=True)
        for target, valid in [("YouTube", True), ("/system/product/app/SomeApp", True),
                              ("/product/app/SomeApp/SomeApp.apk", True),
                              ("/system/priv-app/SystemUI/SystemUI.apk", False),
                              ("/system/app/SomeApp//SomeApp.apk", False),
                              ("/system", False), ("/system/app", False), ("/data/app/X", False),
                              ("../X", False), ("/system/app/../X", False), ("X/file.apk", False),
                              ("*", False), ("$(id)", False), ("X;id", False), ("X'", False),
                              ("X\nY", False), ("SystemUI", False), ("Settings", False),
                              ("FrameworkRes", False), ("com.android.systemui", False)]:
            with self.subTest(target=target):
                result = subprocess.run([BASH, "-c", '. "$1"; COMMONDIR=""; ng_valid_debloat_target "$NG_TEST_TARGET"',
                                         "test", str(GUARD)], env={**os.environ, "NG_TEST_TARGET": target}, capture_output=True, text=True)
                self.assertEqual(valid, result.returncode == 0, result.stderr)

    @unittest.skipUnless(BASH, "POSIX shell is unavailable")
    def test_invalid_late_entry_aborts_before_any_removal_or_property_write(self):
        with tempfile.TemporaryDirectory() as directory:
            config = pathlib.Path(directory) / "debloater.config"
            config.write_text("YouTube\n/system\n")
            script = '''
. "$1"
COMMONDIR=$(cd "$2" && pwd)
debloater_config_file_name="$COMMONDIR/debloater.config"
abort() { echo "$*" >&2; exit 23; }
rm() { echo removal >> "$COMMONDIR/actions"; }
update_prop() { echo property >> "$COMMONDIR/actions"; }
# Emulate an existing safe path while leaving deletion to the real preflight loop.
ng_plan_debloat_path() { printf '/system/app/YouTube\\n' >> "$ng_plan"; }
system=/system; product=/product; system_ext=/system_ext
debloat
'''
            result = subprocess.run([BASH, "-c", script, "test", str(GUARD), directory], capture_output=True, text=True)
            self.assertEqual(23, result.returncode, result.stderr)
            self.assertIn("Unsafe/protected", result.stderr)
            self.assertFalse((pathlib.Path(directory) / "actions").exists())

    @unittest.skipUnless(BASH, "POSIX shell is unavailable")
    def test_selected_packages_are_protected_at_flash_time(self):
        with tempfile.TemporaryDirectory() as directory:
            (pathlib.Path(directory) / "debloater_protected.txt").write_text("YouTube\nDeskClock\n")
            result = subprocess.run([BASH, "-c", '. "$1"; COMMONDIR=$(cd "$2" && pwd); ng_valid_debloat_target youtube',
                "test", str(GUARD), directory], capture_output=True, text=True)
            self.assertNotEqual(0, result.returncode)

    @unittest.skipUnless(BASH, "POSIX shell is unavailable")
    def test_fake_filesystem_symlink_and_removal_failures(self):
        # Filesystem probes and removal are faked for /system. No real system path
        # is created or deleted; only the plan/config live in the disposable dir.
        harness = r'''
. "$1"
COMMONDIR=$(cd "$2" && pwd)
debloater_config_file_name="$COMMONDIR/debloater.config"
system=/system; product=/product; system_ext=/system_ext
abort() { echo "$*" >&2; exit 23; }
function [() {
  case "$*" in
    '-d /system/app ]'|'-d /system/app/YouTube ]') return 0 ;;
    '-e /system/app/YouTube ]'|'-e /system/app/YouTube/YouTube.apk ]') builtin [ "$removed" != 1 ]; return ;;
    '! -e /system/app/YouTube ]'|'! -e /system/app/YouTube/YouTube.apk ]') builtin [ "$removed" = 1 ]; return ;;
    '! -L /system/app/YouTube ]'|'! -L /system/app/YouTube/YouTube.apk ]') builtin [ "$NG_MODE" != symlink ]; return ;;
    '-f /system/app/YouTube/YouTube.apk ]') return 0 ;;
  esac
  builtin [ "$@"
}
readlink() { if [ "$NG_MODE" = redirect ]; then echo /data/app/YouTube; else printf '%s\n' "$2"; fi; }
rm() {
  case "$*" in
    '-rf -- /system/app/YouTube'|'-rf -- /system/app/YouTube/YouTube.apk')
      echo attempted >> "$COMMONDIR/actions"
      [ "$NG_MODE" != failure ] || return 1
      removed=1 ;;
  esac
}
get_prop_file_path() { echo "$COMMONDIR/Debloater.prop"; }
update_prop() { echo property >> "$COMMONDIR/actions"; }
ui_print() { :; }
copy_file() { :; }
debloat
echo complete >> "$COMMONDIR/actions"
'''
        for mode in ("success", "file", "failure", "symlink", "redirect"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as directory:
                root = pathlib.Path(directory)
                (root / "debloater.config").write_text("/system/app/YouTube/YouTube.apk\n" if mode == "file" else "/system/app/YouTube\n")
                (root / "addon.sh").write_text('echo addon >> "$COMMONDIR/actions"\n')
                result = subprocess.run([BASH, "-c", harness, "test", str(GUARD), directory],
                    env={**os.environ, "NG_MODE": mode}, capture_output=True, text=True)
                actions = (root / "actions").read_text() if (root / "actions").exists() else ""
                if mode in {"success", "file"}:
                    self.assertEqual(0, result.returncode, result.stderr)
                    self.assertIn("attempted", actions)
                    self.assertIn("addon", actions)
                    self.assertIn("complete", actions)
                else:
                    self.assertEqual(23, result.returncode, result.stderr)
                    self.assertNotIn("property", actions)
                    self.assertNotIn("addon", actions)
                    self.assertNotIn("complete", actions)
                    if mode in {"symlink", "redirect"}:
                        self.assertNotIn("attempted", actions)
