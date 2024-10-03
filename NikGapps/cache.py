import os
from dotenv import load_dotenv
from NikGapps.build.Build import Build
from NikGapps.config.NikGappsConfig import NikGappsConfig
from niklibrary.helper.F import F
from NikGapps.helper.Package import Package
from niklibrary.compression.Modes import Modes
from NikGapps.helper.compression.CompOps import CompOps
from NikGapps.helper.AppSet import AppSet
from NikGapps.helper import Config
from niklibrary.helper.P import P
from niklibrary.helper.T import T
from niklibrary.helper.SystemStat import SystemStat
from NikGapps.helper.Args import Args
from niklibrary.git.GitOp import GitOp
from niklibrary.git.GitlabManager import GitLabManager


def cache():
    args = Args()
    print("Start of the Program")
    SystemStat.show_stats()
    P.green("---------------------------------------")
    load_dotenv()
    Config.ENVIRONMENT_TYPE = os.getenv("ENVIRONMENT_TYPE") if os.getenv("ENVIRONMENT_TYPE") else "production"
    Config.RELEASE_TYPE = os.getenv("RELEASE_TYPE") if os.getenv("RELEASE_TYPE") else "stable"
    android_versions = [Config.TARGET_ANDROID_VERSION]
    Config.UPLOAD_FILES = args.upload
    if len(args.get_android_versions()) > 0:
        android_versions = args.get_android_versions()
    print("---------------------------------------")
    print("Android Versions to build: " + str(android_versions))
    print("---------------------------------------")
    for android_version in android_versions:
        arch = "arm64"
        url = f"{android_version}{('_' + arch if arch != 'arm64' else '')}_{Config.RELEASE_TYPE}"
        cached_url = url + "_cached"
        gitlab_manager = GitLabManager(private_token=os.getenv("GITLAB_TOKEN"))
        project = gitlab_manager.get_project(cached_url)
        gitattributes = """*.zip filter=lfs diff=lfs merge=lfs -text
        *.tar.xz filter=lfs diff=lfs merge=lfs -text"""
        if project:
            gitlab_manager.reset_repository(cached_url, sleep_for=10, gitattributes=gitattributes)
        else:
            project = gitlab_manager.create_repository(cached_url, provide_owner_access=True)
            gitlab_manager.create_and_commit_file(project_id=project.id, file_path=".gitattributes",
                                                  content=gitattributes)
        repo_cached = GitOp.clone_apk_url(url=cached_url, use_ssh_clone=True)
        apk_repo = GitOp.clone_apk_url(url=url)
        Config.APK_SOURCE = apk_repo.working_tree_dir
        if float(android_version) >= 12.1:
            overlay_repo = GitOp.clone_overlay_repo(android_version=str(android_version), fresh_clone=True)
            Config.OVERLAY_SOURCE = overlay_repo.working_tree_dir
        config_obj = NikGappsConfig(android_version)
        app_set_list = config_obj.package_manager.get_packages("all")
        config_obj.config_package_list = Build.build_from_directory(app_set_list, android_version)
        for appset in config_obj.config_package_list:
            appset: AppSet
            for pkg in appset.package_list:
                pkg: Package
                compression_modes = [Modes.ZIP, Modes.TAR_XZ]
                for mode in compression_modes:
                    t = T()
                    print(f"Compressing into {mode} {pkg.package_title} for {appset.title}")
                    pkg_zip_path = os.path.join(repo_cached.working_tree_dir, appset.title,
                                                f"{pkg.package_title}{mode}")
                    print("Done!") if CompOps.compress_package(pkg_zip_path, pkg, mode) else print("Failed!")
                    t.taken(f"Total time taken to process the {pkg.package_title}, compressing into {mode}")
                repo_cached.git_push(commit_message=f"Compressed {pkg.package_title} for {appset.title}",
                                     push_untracked_files=True, pull_first=True, post_buffer="1048576000")
        if Config.ENVIRONMENT_TYPE.__eq__("production") and F.dir_exists(repo_cached.working_tree_dir):
            F.remove_dir(repo_cached.working_tree_dir)


if __name__ == "__main__":
    cache()
