from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace

from NikGapps.build.Build import Build
from NikGapps.config.NikGappsConfig import NikGappsConfig
from NikGapps.helper import Config
from nikgapps_package_pipeline.apk import Aapt2Inspector
from nikgapps_package_pipeline.errors import PipelineError
from nikgapps_package_pipeline.models import ApkMetadata
from tests_package_pipeline.test_pipeline import apk


class BuildInspectionTests(unittest.TestCase):
    def test_missing_or_non_executable_aapt2_fails_instead_of_returning_error_strings(self):
        for error in (FileNotFoundError('missing aapt2'), PermissionError('not executable')):
            with patch('nikgapps_package_pipeline.apk.subprocess.run', side_effect=error):
                with self.assertRaises(PipelineError):
                    Aapt2Inspector('/sdk/aapt2').inspect(Path('Gms.apk'))

    def test_failed_permission_inspection_propagates_out_of_the_threaded_builder(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            apk(root / 'Core/GmsCore/___priv-app___Gms/Gms.apk')
            appset = NikGappsConfig('17').package_manager.get_packages('core')[0]
            appset.package_list = [p for p in appset.package_list if p.package_title == 'GmsCore']
            with patch.object(Config, 'PACKAGE_SOURCE', 'local'), \
                 patch.object(Config, 'APK_SOURCE', str(root)), \
                 patch.object(Config, 'OVERLAY_SOURCE', str(root / 'overlays')), \
                 patch.object(Config, 'AAPT2', '/sdk/selected-aapt2'), \
                 patch('NikGapps.build.Build.Aapt2Inspector') as inspector:
                inspector.return_value.inspect.return_value = ApkMetadata('com.google.android.gms', '1', 1, 29, 37)
                inspector.return_value.privileged_permissions.side_effect = PipelineError('aapt2 permission inspection failed')
                with self.assertRaisesRegex(PipelineError, 'permission inspection'):
                    Build.build_from_directory([appset], '17')
                inspector.assert_called_once_with('/sdk/selected-aapt2')

    def test_failed_package_inspection_cannot_produce_a_package(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            apk(root / 'Core/GmsCore/___priv-app___Gms/Gms.apk')
            appset = NikGappsConfig('17').package_manager.get_packages('core')[0]
            appset.package_list = [p for p in appset.package_list if p.package_title == 'GmsCore']
            with patch.object(Config, 'PACKAGE_SOURCE', 'local'), \
                 patch.object(Config, 'APK_SOURCE', str(root)), \
                 patch.object(Config, 'OVERLAY_SOURCE', str(root / 'overlays')), \
                 patch('NikGapps.build.Build.Aapt2Inspector') as inspector:
                inspector.return_value.inspect.side_effect = PipelineError('invalid APK')
                with self.assertRaisesRegex(PipelineError, 'invalid APK'):
                    Build.build_from_directory([appset], '17')

    def test_empty_or_unrecognized_permissions_output_cannot_silently_omit_whitelists(self):
        for output in (b'', b"package: com.example\nuses-permission: 'unrecognized'\n"):
            with patch('nikgapps_package_pipeline.apk.subprocess.run', return_value=SimpleNamespace(stdout=output)):
                with self.assertRaises(PipelineError):
                    Aapt2Inspector('/sdk/aapt2').privileged_permissions(Path('App.apk'))
