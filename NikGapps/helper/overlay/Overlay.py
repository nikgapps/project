import os
from NikGapps.helper.Statics import Statics
from NikGapps.helper.overlay.ApkMetaInfo import ApkMetaInfo
from NikGapps.helper.overlay.Manifest import Manifest


class Overlay:
    def __init__(self, apk_name, package_name, android_version, resources):
        self.folder = f"{apk_name}Overlay"
        self.apk_name = f"{self.folder}.apk"
        self.resources = resources
        self.manifest = Manifest(package=package_name, android_version=android_version)
        self.apkMetaInfo = ApkMetaInfo(apk_file_name=self.apk_name, android_version=android_version)

    def build_apk_source(self, source):
        build_dir = source + Statics.dir_sep + self.folder
        self.resources.write(os.path.join(build_dir, 'res/values'), 'config.xml')
        self.manifest.write(build_dir, 'AndroidManifest.xml')
        self.apkMetaInfo.write(build_dir, 'apktool.yml')
