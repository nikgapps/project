import sys
import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch

from NikGapps.helper import Config
from NikGapps.helper.Args import Args


class CliDefaultsTest(unittest.TestCase):
    def test_defaults_follow_config(self):
        with patch.multiple(Config, TARGET_ANDROID_VERSION=16, DEFAULT_PACKAGE_LIST=['core'],
                            PACKAGE_SOURCE='registry', PACKAGE_CHANNEL='stable', PACKAGE_ARCH='arm64'), \
                patch.object(sys, 'argv', ['nikgapps']):
            args = Args()
        self.assertEqual(['16'], args.get_android_versions())
        self.assertEqual(['core'], args.get_package_list())
        self.assertEqual(('registry', 'stable', 'arm64'),
                         (args.package_source, args.package_channel, args.arch))

    def test_arguments_override_config_and_accept_local_sources(self):
        with patch.object(sys, 'argv', ['nikgapps', '--packageSource', 'local',
                                       '--androidVersion', '17', '--packageList', 'basic,full',
                                       '--releaseType', 'beta', '--packageChannel', 'beta', '--arch', 'arm']):
            args = Args()
        self.assertEqual(['17'], args.get_android_versions())
        self.assertEqual(['basic', 'full'], args.get_package_list())
        self.assertEqual(('local', 'beta', 'arm'),
                         (args.package_source, args.package_channel, args.arch))

    def test_local_build_discovers_sources_without_cloning(self):
        import NikGapps.main as builder
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / '17_stable'
            overlays = Path(directory) / 'overlays_17'
            source.mkdir()
            overlays.mkdir()
            def check_sources(*args):
                self.assertEqual(str(source), Config.APK_SOURCE)
                self.assertEqual(str(overlays), Config.OVERLAY_SOURCE)
            with patch.multiple(Config, APK_SOURCE=None, OVERLAY_SOURCE=None,
                                PACKAGE_SOURCE='registry', TARGET_ANDROID_VERSION=16,
                                RELEASE_TYPE='stable', ENVIRONMENT_TYPE='local',
                                USE_CACHED_APKS=False, UPLOAD_FILES=False, OVERRIDE_RELEASE=True), \
                    patch.object(builder.Statics, 'pwd', directory), \
                    patch.object(sys, 'argv', ['nikgapps', '--packageSource', 'local', '--androidVersion', '17']), \
                    patch.object(builder.Release, 'zip', side_effect=check_sources) as build, \
                    patch.object(builder.GitOp, 'clone_apk_source') as clone, \
                    patch.object(builder.GitOp, 'clone_overlay_repo') as clone_overlays, \
                    patch.object(builder.SystemStat, 'show_stats'), patch('builtins.print'):
                builder.main()
                build.assert_called_once_with(['core'], '17', 'arm64', False)
                clone.assert_not_called()
                clone_overlays.assert_not_called()
                self.assertIsNone(Config.APK_SOURCE)
                self.assertIsNone(Config.OVERLAY_SOURCE)

    def test_beta_release_changes_channel_without_a_channel_argument(self):
        with patch.dict('os.environ', {}, clear=True), \
                patch.multiple(Config, RELEASE_TYPE='stable', PACKAGE_CHANNEL='stable', PACKAGE_SOURCE='local'), \
                patch.object(sys, 'argv', ['nikgapps', '--releaseType', 'beta']):
            args = Args()
        self.assertEqual(('beta', 'beta'), (args.release_type, args.package_channel))

    def test_beta_source_path_uses_release_type(self):
        with tempfile.TemporaryDirectory() as directory:
            (Path(directory) / '17_beta').mkdir()
            (Path(directory) / 'overlays_17').mkdir()
            with patch.multiple(Config, RELEASE_TYPE='beta', APK_SOURCE=None, OVERLAY_SOURCE=None):
                source, _ = Config.local_source_paths('17', directory)
            self.assertEqual(str(Path(directory) / '17_beta'), source)


if __name__ == '__main__':
    unittest.main()
