import argparse
import os
from dotenv import load_dotenv
from NikGapps.helper import Config
from niklibrary.helper.SystemStat import SystemStat
from niklibrary.git.GitlabManager import GitLabManager


def copy_repos():
    parser = argparse.ArgumentParser(description='Copy Repos Parser')
    parser.add_argument('-S', '--source', default="", help='Source Repository')
    parser.add_argument('-D', '--destination', default="", help='Destination Repository')
    parser.add_argument('-A', '--android_version', default="", help='Android version')
    args = parser.parse_args()
    android_versions = str(args.android_version).replace("'", "").split(',')
    if not android_versions or (len(android_versions) > 0 and android_versions[0] == ""):
        android_versions = [Config.TARGET_ANDROID_VERSION]
    print("Start of the Program")
    SystemStat.show_stats()
    load_dotenv()
    Config.ENVIRONMENT_TYPE = os.getenv("ENVIRONMENT_TYPE") if os.getenv("ENVIRONMENT_TYPE") else "production"
    Config.RELEASE_TYPE = os.getenv("RELEASE_TYPE") if os.getenv("RELEASE_TYPE") else "stable"

    # Config.UPLOAD_FILES = args.upload
    print("---------------------------------------")
    print("Android Versions to build: " + str(android_versions))
    print("---------------------------------------")

    for android_version in android_versions:
        gitlab_manager = GitLabManager(private_token=os.getenv("GITLAB_TOKEN"))
        gitlab_manager.copy_repository(f"{android_version}_{args.source}", f"{android_version}_{args.destination}",
                                       override_target=True)
        # gitlab_manager.copy_repository(f"{android_version}_stable", f"{android_version}_ondemand", override_target=True)
        # gitlab_manager.copy_repository(f"{android_version}_stable_cached", f"{android_version}_ondemand_cached",
        #                                override_target=True)


if __name__ == "__main__":
    copy_repos()
