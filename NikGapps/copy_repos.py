import os
from dotenv import load_dotenv
from NikGapps.helper.Args import Args
from NikGapps.helper import Config
from NikGapps.helper.SystemStat import SystemStat
from NikGapps.helper.git.GitlabManager import GitLabManager


def copy_repos():
    args = Args()
    print("Start of the Program")
    SystemStat.show_stats()
    load_dotenv()
    Config.ENVIRONMENT_TYPE = os.getenv("ENVIRONMENT_TYPE") if os.getenv("ENVIRONMENT_TYPE") else "production"
    Config.RELEASE_TYPE = os.getenv("RELEASE_TYPE") if os.getenv("RELEASE_TYPE") else "stable"
    android_versions = [Config.TARGET_ANDROID_VERSION]
    if len(args.get_android_versions()) > 0:
        android_versions = args.get_android_versions()
    Config.UPLOAD_FILES = args.upload
    print("---------------------------------------")
    print("Android Versions to build: " + str(android_versions))
    print("---------------------------------------")

    for android_version in android_versions:
        gitlab_manager = GitLabManager(private_token=os.getenv("GITLAB_TOKEN"))
        gitlab_manager.copy_repository(f"{android_version}_stable", f"{android_version}_ondemand", override_target=True)
        gitlab_manager.copy_repository(f"{android_version}_stable_cached", f"{android_version}_ondemand_cached",
                                       override_target=True)


if __name__ == "__main__":
    copy_repos()
