import os
from NikGapps.helper.Args import Args
from NikGapps.helper import Config
from NikGapps.helper.git.GitlabManager import GitLabManager


def copy_repos():
    args = Args()
    android_versions = [Config.TARGET_ANDROID_VERSION]
    if len(args.get_android_versions()) > 0:
        android_versions = args.get_android_versions()

    for android_version in android_versions:
        gitlab_manager = GitLabManager(private_token=os.getenv("GITLAB_TOKEN"))
        gitlab_manager.copy_repository(f"{android_version}_stable", f"{android_version}_ondemand", override_target=True)


if __name__ == "__main__":
    copy_repos()
