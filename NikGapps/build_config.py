import os
from dotenv import load_dotenv

from NikGapps.build.Build import Build
from NikGapps.config.NikGappsConfig import NikGappsConfig
from NikGapps.helper.Args import Args
from NikGapps.helper import Config
from niklibrary.helper.B64 import B64
from niklibrary.helper.F import F
from niklibrary.helper.Statics import Statics
from niklibrary.helper.SystemStat import SystemStat
from niklibrary.helper.T import T
from NikGapps.helper.compression.Export import Export
from niklibrary.compression.Modes import Modes
from niklibrary.git.GitOp import GitOp


def build_config():
    args = Args()
    print("Start of the Program")
    SystemStat.show_stats()
    load_dotenv()
    Config.ENVIRONMENT_TYPE = os.getenv("ENVIRONMENT_TYPE") if os.getenv("ENVIRONMENT_TYPE") else "dev"
    Config.RELEASE_TYPE = os.getenv("RELEASE_TYPE") if os.getenv("RELEASE_TYPE") else "stable"
    android_versions = [Config.TARGET_ANDROID_VERSION]
    if len(args.get_android_versions()) > 0:
        android_versions = args.get_android_versions()
    Config.UPLOAD_FILES = args.upload
    print("---------------------------------------")
    print("Android Versions to build: " + str(android_versions))
    print("---------------------------------------")
    config_name = args.config_name
    if config_name is None:
        print("Please provide config name")
        exit(1)
    if not str(config_name).endswith(".config"):
        config_name = config_name + ".config"
    if F.file_exists(config_name):
        print("Reading from the file " + config_name)
        path = config_name
    else:
        config_value = args.config_value
        if config_value is None:
            print("Please provide config value")
            exit(1)
        else:
            config_string = B64.b64d(config_value)
            path = config_name
            F.write_string_in_lf_file(str_data=config_string, file_path=path)
    for android_version in android_versions:
        apk_repo = GitOp.clone_apk_source(android_version, args.arch, release_type=Config.RELEASE_TYPE)
        Config.APK_SOURCE = apk_repo.working_tree_dir
        overlay_repo = GitOp.clone_overlay_repo(android_version)
        Config.OVERLAY_SOURCE = overlay_repo.working_tree_dir
        config_obj = NikGappsConfig(android_version=android_version, config_path=path)
        print(f"Setting up package list from {config_name}...")
        config_obj.config_package_list = Build.build_from_directory(app_set_build_list=config_obj.config_package_list,
                                                                    android_version=android_version)
        file_name = Statics.get_release_directory(android_version) + Statics.dir_sep + T.get_file_name(
            config_obj.config_name, android_version)
        z = Export(file_name, sign=False)
        file_name, zip_execution_status = z.zip(config_obj=config_obj,
                                                compression_mode=Modes.DEFAULT, send_zip_device=args.send_zip_device)
        if zip_execution_status:
            print("The zip file is created successfully")
        else:
            print("Failed to create the zip file")


if __name__ == "__main__":
    build_config()
