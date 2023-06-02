import os
import yaml

from NikGapps.helper.Statics import Statics


class ApkMetaInfo:
    def __init__(self, apkFileName, android_version):
        self.apkFileName = apkFileName
        self.minSdkVersion = Statics.get_android_sdk(android_version)
        self.targetSdkVersion = self.minSdkVersion
        self.versionCode = self.minSdkVersion
        self.versionName = android_version

    def to_dict(self):
        return {
            '!!brut.androlib.meta.MetaInfo': None,
            'apkFileName': self.apkFileName,
            'compressionType': False,
            'doNotCompress': ['resources.arsc'],
            'isFrameworkApk': False,
            'packageInfo': {
                'forcedPackageId': '127',
                'renameManifestPackage': None,
            },
            'sdkInfo': {
                'minSdkVersion': self.minSdkVersion,
                'targetSdkVersion': self.targetSdkVersion,
            },
            'sharedLibrary': False,
            'sparseResources': False,
            'unknownFiles': {},
            'usesFramework': {
                'ids': [1],
                'tag': None,
            },
            'version': '1.0.0',
            'versionInfo': {
                'versionCode': self.versionCode,
                'versionName': self.versionName,
            }
        }

    def write(self, directory, filename):
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(os.path.join(directory, filename), 'w') as file:
            yaml.dump(self.to_dict(), file)

