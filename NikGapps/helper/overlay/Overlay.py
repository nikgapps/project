import os
from NikGapps.helper.Statics import Statics
from NikGapps.helper.overlay.ApkMetaInfo import ApkMetaInfo
from NikGapps.helper.overlay.Manifest import Manifest


class Overlay:
    def __init__(self, apkName, package_name, android_version, resources):
        self.folder = f"{apkName}Overlay"
        self.apk_name = f"{self.folder}.apk"
        self.resources = resources
        self.manifest = Manifest(package=package_name, android_version=android_version)
        self.apkMetaInfo = ApkMetaInfo(apkFileName=self.apk_name, android_version=android_version)

    def build_apk_source(self, source):
        build_dir = source + Statics.dir_sep + self.folder
        self.resources.write(os.path.join(build_dir, 'res/values'), 'config.xml')
        self.manifest.write(build_dir, 'AndroidManifest.xml')
        self.apkMetaInfo.write(build_dir, 'apktool.yml')
