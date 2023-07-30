# from NikGapps.helper.NikGappsConfig import NikGappsConfig
from NikGapps.helper.NikGappsConfig import NikGappsConfig
from NikGapps.helper.git.GitOperations import GitOperations
from NikGapps.helper.web.TelegramApi import TelegramApi
from NikGapps.helper.upload.Upload import Upload
from NikGapps.build.Release import Release
from NikGapps.helper.Config import FETCH_PACKAGE
from NikGapps.helper import Config


class Operation:

    @staticmethod
    def fetch(android_versions):
        for android_version in android_versions:
            pkg_list = Release.package(FETCH_PACKAGE, android_version)
            if pkg_list.__len__() > 0:
                message = "Packages Successfully Fetched"
                print(message)
            else:
                message = "Fetching Failed"
                print(message)

    @staticmethod
    def build(android_versions, telegram: TelegramApi, arch="arm64", git_clone=Config.GIT_CLONE_SOURCE,
              package_list=Config.BUILD_PACKAGE_LIST, sign_zip=Config.SIGN_ZIP, send_zip_device=Config.SEND_ZIP_DEVICE,
              fresh_build=Config.FRESH_BUILD, is_release=False):
        for android_version in android_versions:
            upload = Upload(android_version=android_version, upload_files=Config.UPLOAD_FILES,
                            release_type=Config.RELEASE_TYPE)
            Config.TARGET_ANDROID_VERSION = android_version
            # clone the apk repo if it doesn't exist
            if git_clone:
                GitOperations.clone_apk_repo(android_version, arch, branch="main" if Config.RELEASE_TYPE.__eq__(
                    "stable") else "canary")
                GitOperations.clone_overlay_repo(android_version)
            if Config.OVERRIDE_RELEASE:
                Release.zip(package_list, android_version, arch, sign_zip, send_zip_device, fresh_build, telegram, upload)
            upload.close_connection()
            if Config.UPLOAD_FILES:
                config = NikGappsConfig(android_version=android_version)
                config.upload_nikgapps_config()
            if is_release:
                GitOperations.mark_a_release(android_version, Config.RELEASE_TYPE)
