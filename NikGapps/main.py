#!/usr/bin/env python
from NikGapps.build.Release import Release
from NikGapps.helper.Args import Args
from NikGapps.helper import Config
from NikGapps.helper.Json import Json
from NikGapps.helper.Statics import Statics
from NikGapps.helper.SystemStat import SystemStat
from NikGapps.helper.P import P
from NikGapps.helper.T import T
from NikGapps.helper.compression.Modes import Modes
from NikGapps.helper.git.GitOperations import GitOperations
from NikGapps.helper.upload.Upload import Upload
from NikGapps.helper.web.Requests import Requests
from NikGapps.helper.web.TelegramApi import TelegramApi


def main():
    args = Args()
    print("Start of the Program")
    SystemStat.show_stats()
    t = T()
    P.green("---------------------------------------")

    android_versions = [Config.TARGET_ANDROID_VERSION]
    package_list = Config.BUILD_PACKAGE_LIST
    Config.UPLOAD_FILES = args.upload
    Config.USE_CACHED_APKS = args.use_cached_apks
    if Config.USE_CACHED_APKS:
        print("Using Cached Apks")
    Modes.DEFAULT = Modes.TAR_XZ if args.tar else Modes.ZIP
    if len(args.get_package_list()) > 0:
        package_list = args.get_package_list()

    if len(args.get_android_versions()) > 0:
        android_versions = args.get_android_versions()
    print("---------------------------------------")
    print("Android Versions to build: " + str(android_versions))
    print("---------------------------------------")
    print("Packages to build: " + str(package_list))
    print("---------------------------------------")

    telegram = TelegramApi(Config.TELEGRAM_BOT_TOKEN, Config.TELEGRAM_CHAT_ID)
    for android_version in android_versions:
        Json.write_dict_to_file(Requests.get_package_details(), Statics.get_package_details(android_version))
        Statics.package_details = Json.read_dict_from_file(Statics.get_package_details(android_version))
        upload = Upload(android_version=android_version, upload_files=Config.UPLOAD_FILES,
                        release_type=Config.RELEASE_TYPE)
        Config.TARGET_ANDROID_VERSION = android_version
        # clone the apk repo if it doesn't exist
        if args.enable_git_clone:
            GitOperations.clone_apk_repo(android_version, args.arch, branch="main" if Config.RELEASE_TYPE.__eq__(
                "stable") else "canary")
            GitOperations.clone_overlay_repo(android_version)
            if Config.USE_CACHED_APKS:
                GitOperations.clone_apk_repo(android_version, branch="main", cached=True)
        if Config.OVERRIDE_RELEASE:
            Release.zip(package_list, android_version, args.arch, args.sign, Config.SEND_ZIP_DEVICE, Config.FRESH_BUILD, telegram,
                        upload)
        upload.close_connection()
        if Config.RELEASE_TYPE:
            GitOperations.mark_a_release(android_version, Config.RELEASE_TYPE)
    if args.release:
        if args.update_website:
            website_repo = GitOperations.get_website_repo_for_changelog()
            if website_repo is not None:
                website_repo.update_changelog()

    t.taken("Total time taken by the program")

    print("End of the Program")


if __name__ == '__main__':
    main()
