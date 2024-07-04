#!/usr/bin/env python
import os
from dotenv import load_dotenv
from NikGapps.build.Release import Release
from NikGapps.helper.Args import Args
from NikGapps.helper import Config
from NikGapps.helper.SystemStat import SystemStat
from NikGapps.helper.P import P
from NikGapps.helper.T import T
from NikGapps.helper.compression.Modes import Modes
from NikGapps.helper.git.GitOperations import GitOperations


def main():
    args = Args()
    print("Start of the Program")
    SystemStat.show_stats()
    t = T()
    P.green("---------------------------------------")
    load_dotenv()
    Config.ENVIRONMENT_TYPE = os.getenv("ENVIRONMENT_TYPE") if os.getenv(
        "ENVIRONMENT_TYPE") is not None else "production"
    Config.RELEASE_TYPE = os.getenv("RELEASE_TYPE") if os.getenv("RELEASE_TYPE") is not None else "stable"
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

    for android_version in android_versions:
        Config.TARGET_ANDROID_VERSION = android_version
        # clone the apk repo if it doesn't exist
        if args.enable_git_clone:
            if Config.USE_CACHED_APKS:
                GitOperations.clone_apk_repo(android_version, branch="main", cached=True)
            else:
                GitOperations.clone_apk_repo(android_version, args.arch, branch="main")
                # GitOperations.clone_apk_source(android_version, args.arch, release_type=Config.RELEASE_TYPE)
                GitOperations.clone_overlay_repo(android_version)
        if Config.OVERRIDE_RELEASE:
            Release.zip(package_list, android_version, args.arch, args.sign)
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
