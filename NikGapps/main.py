#!/usr/bin/env python
from niklibrary.git.GitStatics import GitStatics

from NikGapps.build.Release import Release
from NikGapps.helper.Args import Args
from NikGapps.helper import Config
from niklibrary.helper.SystemStat import SystemStat
from niklibrary.helper.T import T
from niklibrary.compression.Modes import Modes
from niklibrary.git.GitOp import GitOp

from NikGapps.helper.git.TestGit import TestGit


def main():
    args = Args()
    print("Start of the Program")
    SystemStat.show_stats()
    t = T()
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
                cached_repo = GitOp.clone_apk_source(android_version, release_type=Config.RELEASE_TYPE,
                                                             cached=True)
                Config.CACHED_SOURCE = cached_repo.working_tree_dir
            else:
                apk_repo = GitOp.clone_apk_source(android_version, args.arch, release_type=Config.RELEASE_TYPE)
                Config.APK_SOURCE = apk_repo.working_tree_dir
                overlay_repo = GitOp.clone_overlay_repo(android_version)
                if overlay_repo is not None:
                    Config.OVERLAY_SOURCE = overlay_repo.working_tree_dir
        if Config.OVERRIDE_RELEASE:
            Release.zip(package_list, android_version, args.arch, args.sign)
        if Config.RELEASE_TYPE and Config.ENVIRONMENT_TYPE == "production":
            GitOp.mark_a_release(android_version, Config.RELEASE_TYPE)
    if args.release:
        if args.update_website:
            website_repo = TestGit(GitStatics.website_repo_dir)
            if GitStatics.website_repo_url is not None:
                website_repo.clone_repo(repo_url=GitStatics.website_repo_url, fresh_clone=False, branch="main")
            if website_repo is not None:
                website_repo.update_changelog()

    t.taken("Total time taken by the program")

    print("End of the Program")


if __name__ == '__main__':
    main()
