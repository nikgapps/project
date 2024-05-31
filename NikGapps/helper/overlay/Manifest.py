import os
import xml.etree.ElementTree as eT

from NikGapps.helper.Statics import Statics


class Manifest:
    def __init__(self, package, android_version, target_package="android", priority="1337",
                 is_static=True):
        self.package = package
        self.compileSdkVersion = Statics.get_android_sdk(android_version)
        self.compileSdkVersionCodename = android_version
        self.platformBuildVersionCode = Statics.get_android_sdk(android_version)
        self.platformBuildVersionName = android_version
        self.targetPackage = target_package
        self.priority = priority
        self.isStatic = str(is_static).lower()

    def to_xml(self):
        root = eT.Element('manifest',
                          {'xmlns:android': 'http://schemas.android.com/apk/res/android',
                           'package': self.package,
                           'android:compileSdkVersion': self.compileSdkVersion,
                           'android:compileSdkVersionCodename': self.compileSdkVersionCodename,
                           'platformBuildVersionCode': self.platformBuildVersionCode,
                           'platformBuildVersionName': self.platformBuildVersionName})

        eT.SubElement(root, 'application',
                      {'android:extractNativeLibs': 'true', 'android:hasCode': 'false'})
        eT.SubElement(root, 'overlay',
                      {'android:targetPackage': self.targetPackage,
                       'android:priority': self.priority, 'android:isStatic': self.isStatic})
        return eT.ElementTree(root)

    def indent(self, elem, level=0):
        i = "\n" + level * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                self.indent(elem, level + 1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i

    def write(self, directory, filename):
        if not os.path.exists(directory):
            os.makedirs(directory)
        root = self.to_xml().getroot()
        self.indent(root)
        eT.ElementTree(root).write(os.path.join(directory, filename),
                                   encoding="utf-8", xml_declaration=False)
