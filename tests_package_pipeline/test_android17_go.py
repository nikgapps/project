import json
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET
import zipfile
from unittest.mock import patch
from types import SimpleNamespace

from NikGapps.build.GoSupport import generated_go_files, core_source_appset
from NikGapps.config.NikGappsConfig import NikGappsConfig
from nikgapps_package_pipeline.config import PipelineConfig
from nikgapps_package_pipeline.pipeline import MigrationPipeline
from nikgapps_package_pipeline.scanner import LegacyRepositoryScanner
from tests_package_pipeline.test_pipeline import FakeInspector, apk


class Android17GoTests(unittest.TestCase):
    def test_local_stable_builder_generates_go_files_from_core_only(self):
        from NikGapps.build.Build import Build
        from NikGapps.helper import Config
        from niklibrary.helper.Statics import Statics

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            gms = self.source(root / 'source')
            before = {p.relative_to(gms).as_posix(): p.read_bytes() for p in gms.rglob('*') if p.is_file()}
            manager = NikGappsConfig('17').package_manager
            appset = manager.get_packages('corego')[0]
            appset.package_list = [p for p in appset.package_list if p.package_title == 'GmsCore']
            with patch.object(Config, 'PACKAGE_SOURCE', 'local'), \
                 patch.object(Config, 'APK_SOURCE', str(root / 'source')), \
                 patch.object(Config, 'OVERLAY_SOURCE', str(root / 'overlays')), \
                 patch.object(Statics, 'get_temp_packages_directory', return_value=str(root / 'temp')), \
                 patch('NikGapps.build.Build.Aapt2Inspector') as inspector:
                inspector.return_value.inspect.return_value = SimpleNamespace(package_name='com.google.android.gms')
                inspector.return_value.privileged_permissions.return_value = []
                package = Build.build_from_directory([appset], '17')[0].package_list[0]
            files = {value: Path(key) for key, value in package.file_dict.items()}
            self.assertIn('___etc___sysconfig/google_go.xml', files)
            self.assertIn('___etc___sysconfig/gmsexpress.xml', files)
            self.assertIn('___etc___sysconfig/google_dialergo_experience.xml', files)
            permissions = files['___etc___permissions/NikGapps-privapp-permissions-google-p.xml'].read_text()
            self.assertNotIn('KEEP_ON_CORE', permissions)
            self.assertIn('KEEP_ON_BOTH', permissions)
            self.assertEqual(gms / '___priv-app___Gms/Gms.apk', files['___priv-app___Gms/Gms.apk'])
            self.assertEqual(before, {p.relative_to(gms).as_posix(): p.read_bytes() for p in gms.rglob('*') if p.is_file()})
            self.assertFalse((root / 'source/CoreGo').exists())

    def test_overlay_install_order_matches_for_raw_and_prepared_registry_sources(self):
        from NikGapps.build.Build import Build
        from NikGapps.helper import Config
        import shutil

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.source(root / 'source')
            overlay = root / 'overlays/GmsCoreOverlay/GmsCoreOverlay.apk'
            overlay.parent.mkdir(parents=True)
            overlay.write_bytes(b'overlay')
            shutil.copytree(root / 'source/Core', root / 'prepared/Core')
            prepared_overlay = root / 'prepared/Core/GmsCore/___overlay/GmsCoreOverlay.apk'
            prepared_overlay.parent.mkdir()
            prepared_overlay.write_bytes(b'overlay')
            appset = NikGappsConfig('17').package_manager.get_packages('core')[0]
            appset.package_list = [p for p in appset.package_list if p.package_title == 'GmsCore']
            with patch.object(Config, 'APK_SOURCE', str(root / 'source')), \
                 patch.object(Config, 'OVERLAY_SOURCE', str(root / 'overlays')), \
                 patch('NikGapps.build.Build.Aapt2Inspector') as inspector, \
                 patch('nikgapps_package_pipeline.consumer.CatalogPackageSource') as consumer:
                inspector.return_value.inspect.return_value = SimpleNamespace(package_name='com.google.android.gms')
                inspector.return_value.privileged_permissions.return_value = []
                consumer.return_value.prepare.return_value = root / 'prepared'
                with patch.object(Config, 'PACKAGE_SOURCE', 'local'):
                    raw = Build.build_from_directory([appset], '17')[0].package_list[0]
                with patch.object(Config, 'PACKAGE_SOURCE', 'registry'), \
                     patch.object(Config, 'OVERLAY_SOURCE', str(root / 'empty')):
                    registry = Build.build_from_directory([appset], '17')[0].package_list[0]
            self.assertEqual(raw.install_list, registry.install_list)
            self.assertEqual(list(raw.file_dict.values()), list(registry.file_dict.values()))

    def source(self, root):
        gms = root / 'Core/GmsCore'
        apk(gms / '___priv-app___Gms/Gms.apk')
        xml = gms / '___etc___permissions/NikGapps-privapp-permissions-google-p.xml'
        xml.parent.mkdir()
        xml.write_text('<permissions><privapp-permissions package="com.google.android.apps.nexuslauncher"><permission name="KEEP_ON_CORE"/></privapp-permissions><privapp-permissions package="com.google.android.apps.aiwallpapers"><permission name="android.permission.CONFIGURE_WALLPAPERS"/><permission name="KEEP_ON_BOTH"/></privapp-permissions></permissions>')
        return gms

    def test_config42_has_corego_without_extra_files_but_16_keeps_legacy_packages(self):
        current = NikGappsConfig('17')
        text = current.get_nikgapps_config()
        self.assertIn('Version=42', text)
        self.assertIn('CoreGo=', text)
        self.assertNotIn('>>ExtraFiles=', text)
        self.assertNotIn('>>ExtraFilesGo=', text)
        self.assertEqual(['GmsCore', 'GooglePlayStore', 'GoogleServicesFramework'],
                         [p.package_title for p in current.package_manager.get_packages('corego')[0].package_list])
        legacy = NikGappsConfig('16').get_nikgapps_config()
        self.assertIn('Version=38', legacy)
        self.assertIn('>>ExtraFiles=', legacy)
        self.assertIn('ExtraFilesGo', [p.package_title for p in NikGappsConfig('16').package_manager.get_packages('corego')[0].package_list])

    def test_one_core_source_produces_two_complete_registry_artifacts(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            gms = self.source(root / 'source')
            before = {p.relative_to(gms).as_posix(): p.read_bytes() for p in gms.rglob('*') if p.is_file()}
            packages = MigrationPipeline(LegacyRepositoryScanner(), FakeInspector()).migrate(
                root / 'source', root / 'output', PipelineConfig(android_version='17', platform_api=37),
                artifact_base_url='https://gitlab.test/packages/generic')
            self.assertEqual({'gms_core_android17', 'gms_core_go_android17'}, {p.package_id for p in packages})
            for p in packages:
                self.assertEqual([], p.dependencies)
                self.assertEqual('05', p.descriptor['install']['addonIndex'])
                with zipfile.ZipFile(p.artifact_path) as archive:
                    self.assertIn('___priv-app___Gms/Gms.apk', archive.namelist())
                    self.assertIn('com.google.android.dialer.support', archive.read('installer.sh').decode())
                    is_go = p.package_id == 'gms_core_go_android17'
                    self.assertEqual(is_go, '___etc___sysconfig/google_go.xml' in archive.namelist())
                    permissions = archive.read('___etc___permissions/NikGapps-privapp-permissions-google-p.xml').decode()
                    self.assertEqual(not is_go, 'KEEP_ON_CORE' in permissions)
                    self.assertIn('KEEP_ON_BOTH', permissions)
            self.assertEqual(before, {p.relative_to(gms).as_posix(): p.read_bytes() for p in gms.rglob('*') if p.is_file()})
            self.assertFalse((root / 'source/CoreGo').exists())

    def test_corego_source_alias_is_version_gated(self):
        self.assertEqual('Core', core_source_appset('CoreGo', 'GmsCore', '17'))
        self.assertEqual('CoreGo', core_source_appset('CoreGo', 'GmsCore', '16'))
        self.assertEqual('GoogleGo', core_source_appset('GoogleGo', 'GoogleGo', '17'))

    def test_17_catalog_preserves_legacy_package_dependency_contract(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.source(root / 'source')
            output = root / 'output'
            metadata = output / 'metadata'
            metadata.mkdir(parents=True)
            old = {'id': 'gms_core', 'appSets': ['core'], 'legacy': {'memberships': ['Core/GmsCore']},
                   'dependencies': [{'id': 'gms_core_extra_files'}], 'versions': {'old': {'supportedAndroidVersions': ['16']}},
                   'channels': {'stable': 'old'}}
            (metadata / 'catalog.json').write_text(json.dumps({'schemaVersion': 1, 'androidVersion': '16', 'platformApi': 36,
                'architecture': 'arm64-v8a', 'channel': 'stable', 'packages': [old]}))
            MigrationPipeline(LegacyRepositoryScanner(), FakeInspector()).migrate(root / 'source', output,
                PipelineConfig(android_version='17', platform_api=37), artifact_base_url='https://gitlab.test/packages/generic')
            saved = json.loads((metadata / 'catalog.json').read_text())
            retained = next(p for p in saved['packages'] if p['id'] == 'gms_core')
            self.assertEqual(old, retained)


if __name__ == '__main__':
    unittest.main()
