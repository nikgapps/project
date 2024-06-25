import json
from pathlib import Path

from NikGapps.build.NikGappsManager import NikGappsManager
from NikGapps.helper import Config
from NikGapps.helper.AppSet import AppSet
from NikGapps.helper.Assets import Assets
from NikGapps.helper.ConfigObj import ConfigObj
from NikGapps.helper.FileOp import FileOp
from NikGapps.helper.Package import Package
from NikGapps.helper.Statics import Statics
from NikGapps.helper.git.GitOperations import GitOperations
from NikGapps.helper.upload.Upload import Upload
from NikGapps.helper.web.Requests import Requests


class NikGappsConfig:
    def __init__(self, android_version=None, config_path=None, raw_config=None,
                 config_name=None,
                 use_zip_config=0):
        self.is_elite = False
        self.creator = "Nikhil Menghani"
        self.package_manager = NikGappsManager(android_version)
        self.android_version = android_version
        self.arch = "arm64"
        self.config_version = Assets.config_versions[self.android_version]
        self.config_path = config_path
        self.use_zip_config = use_zip_config
        self.elite_folder = None
        if config_path is not None:
            self.raw_config = "".join(FileOp.read_string_file(config_path))
            self.config_name = str(Path(self.config_path).name).split(".config")[0]
            if str(self.config_path).__contains__(Statics.dir_sep + "elite" + Statics.dir_sep):
                self.is_elite = True
                self.elite_folder = str(self.config_path).split(Statics.dir_sep)[-2]
                self.creator = Requests.get_folder_access(self.elite_folder)
        else:
            self.raw_config = raw_config if raw_config is not None else self.build_default_nikgapps_config()
            self.config_name = "nikgapps" if config_name is None else config_name
        self.config_dict = self.build_config_dict()
        self.config_objects = self.build_config_objects(self.config_dict)
        self.config_package_list = self.get_config_packages()
        self.debloater_list = self.get_debloater_list()

    def build_config_dict(self):
        lines = {}
        for line in self.raw_config.splitlines():
            if line.__eq__('') or line.__eq__('\n') or line.startswith('#') \
                    or line.startswith("File Not Found") \
                    or line.startswith("UseZipConfig=") \
                    or not line.__contains__("="):
                continue
            lines[line.split('=')[0]] = line.split('=')[1].replace('\n', '')
        return lines

    def build_config_objects(self, config_dict=None):
        config_list = []
        default_mode, install_mode = "default", "install"
        enabled_mode, disabled_mode, use_zip_config = 1, 0, self.use_zip_config
        predefined_configs = {
            "AndroidVersion": self.android_version,
            "Version": self.config_version,
            "LogDirectory": {
                "value": default_mode,
                "description": """# set this to the directory you want to copy the logs to.
# for e.g. LogDirectory="/system/etc" will install the logs to /system/etc/nikgapps_logs directory
# by default it will install it to /sdcard/NikGapps/nikgapps_logs"""
            },
            "InstallPartition": {
                "value": default_mode,
                "description": "# set to /system, /product or /system_ext if you want to force the installation to aforementioned locations"
            },
            "Mode": {
                "value": install_mode,
                "description": "# set to uninstall if you want to uninstall any google app, also set the value of google app below to -1"
            },
            "WipeDalvikCache": {
                "value": enabled_mode,
                "description": "# set WipeDalvikCache=0 if you don't want the installer to wipe dalvik/cache after installing the gapps"
            },
            "WipeRuntimePermissions": {
                "value": disabled_mode,
                "description": "# set WipeRuntimePermissions=1 if you want to wipe runtime permissions"
            },
            "ExecuteBackupRestore": {
                "value": enabled_mode,
                "description": "# Addon.d config, set it to 0 to skip the automatic backup/restore while flashing the rom"
            },
            "UseZipConfig": {
                "value": use_zip_config,
                "description": "# if you want to force the installer to use the config from gapps zip file, set below to 1"
            },
            "OverwriteWithZipConfig": {
                "value": disabled_mode,
                "description": "# if you want to overwrite the config located in /sdcard/NikGapps with gapps zip file, set below to 1. Applicable to decrypted storage only"
            },
            "GmsOptimization": {
                "value": disabled_mode,
                "description": "# set this to 1 if you want to enable gms optimization, careful while doing it, you may experience issues like delayed notification with some Roms"
            },
            "GenerateLogs": {
                "value": enabled_mode,
                "description": "# set this to 0 if you want to skip generating nikgapps logs, if you run into issues, enable it and flash the zip again to get the logs"
            }
        }
        if config_dict is not None:
            cutoff_index = list(config_dict.keys()).index("Core") if "Core" in config_dict else len(config_dict)
            for key, value in list(config_dict.items())[:cutoff_index]:
                if key in predefined_configs:
                    continue
                config_list.append(ConfigObj(key, value))
        config_list.extend(
            ConfigObj(key, config_info["value"], config_info.get("description")) if isinstance(config_info, dict)
            else ConfigObj(key, config_info)
            for key, config_info in predefined_configs.items()
        )
        return config_list

    def build_default_nikgapps_config(self):
        nikgapps_config_lines = "# NikGapps configuration file\n\n"
        nikgapps_config_lines += "# If you are not sure about the config, " \
                                 "just skip making changes to it or comment it by adding # before it\n"
        nikgapps_config_lines += "# visit https://nikgapps.com/misc/2022/02/22/" \
                                 "NikGapps-Config.html to read everything about nikgapps\n\n"

        for config_obj in self.build_config_objects():
            nikgapps_config_lines += config_obj.get_string()

        nikgapps_config_lines += "# Following are the packages with default configuration\n"

        for app_set in self.package_manager.get_packages("full"):
            if len(app_set.package_list) > 1:
                nikgapps_config_lines += "\n# Set " + app_set.title + "=0 if you want to skip installing all " \
                                                                      "packages belonging to " \
                                                                      "" + app_set.title + " Package\n"
                nikgapps_config_lines += app_set.title + "=" + "1" + "\n"
                for pkg in app_set.package_list:
                    nikgapps_config_lines += ">>" + pkg.package_title + "=" + str(pkg.enabled) + "\n"
                nikgapps_config_lines += "\n"
            else:
                for pkg in app_set.package_list:
                    nikgapps_config_lines += pkg.package_title + "=" + str(pkg.enabled) + "\n"
        for app_set in self.package_manager.get_packages("go"):
            if len(app_set.package_list) > 1:
                nikgapps_config_lines += "\n# Set " + app_set.title + "=0 if you want to skip installing all " \
                                                                      "packages belonging to " \
                                                                      "" + app_set.title + " Package\n"
                nikgapps_config_lines += app_set.title + "=" + "1" + "\n\n"
                nikgapps_config_lines += "# Setting CoreGo=0 will not skip following packages," \
                                         " set them to 0 if you want to skip them  \n"
            else:
                nikgapps_config_lines += app_set.title + "=" + "1" + "\n"
        nikgapps_config_lines += "\n"
        nikgapps_config_lines += "# Following are the Addon packages NikGapps supports\n"
        for app_set in self.package_manager.get_packages("addons"):
            nikgapps_config_lines += app_set.title + "=" + "1" + "\n"
        return nikgapps_config_lines

    def get_config_packages(self):
        config_dict = self.config_dict
        app_set_list = []
        pre_defined_addons = {addon.title for addon in self.package_manager.get_packages("addons")}
        for app_set in self.package_manager.get_packages("all"):
            app_set: AppSet
            app_set_title = app_set.title
            app_set_config_value = self.config_dict.get(app_set_title)
            if not app_set_config_value:
                continue
            pkg_len = len(app_set.package_list)
            new_app_set = None
            if pkg_len > 1 and str(app_set_config_value) == "1":
                new_app_set = AppSet(app_set.title)
                for pkg in app_set.package_list:
                    pkg: Package
                    if app_set.title.lower() == "corego":
                        new_app_set.add_package(pkg)
                        if pkg.package_title != "ExtraFilesGo":
                            self.config_dict[str(">>" + pkg.package_title)] = "1"
                        continue
                    if str(">>" + pkg.package_title) not in config_dict:
                        if app_set.title in pre_defined_addons:
                            new_app_set.add_package(pkg)
                        continue
                    if config_dict[str(">>" + pkg.package_title)] in ("1", "2"):
                        new_app_set.add_package(pkg)
                    else:
                        print("Package disabled " + pkg.package_title)
            elif pkg_len == 1 and str(config_dict[app_set.title]) in ("1", "2"):
                new_app_set = app_set
            if new_app_set is not None:
                app_set_list.append(new_app_set)
        return app_set_list

    def get_nikgapps_config(self, config_dict=None, config_objects=None, for_release=False):
        nikgapps_config_lines = "# NikGapps configuration file\n\n"
        nikgapps_config_lines += "# If you are not sure about the config, " \
                                 "just skip making changes to it or comment it by adding # before it\n"
        nikgapps_config_lines += "# visit https://nikgapps.com/misc/2022/02/22/" \
                                 "NikGapps-Config.html to read everything about nikgapps\n\n"

        for config_obj in self.config_objects if config_objects is None else config_objects:
            nikgapps_config_lines += config_obj.get_string()

        nikgapps_config_lines += "# Following are the packages with default configuration\n"
        config_dict = self.config_dict if config_dict is None else config_dict
        for app_set in self.package_manager.get_packages("full"):
            if len(app_set.package_list) > 1:
                nikgapps_config_lines += "\n# Set " + app_set.title + "=0 if you want to skip installing all " \
                                                                      "packages belonging to " \
                                                                      "" + app_set.title + " Package\n"
                nikgapps_config_lines += app_set.title + "=" + config_dict.get(app_set.title, "0") + "\n"
                for pkg in app_set.package_list:
                    entry = ">>" + pkg.package_title
                    nikgapps_config_lines += entry + "=" + config_dict.get(entry, "0") + "\n"
                nikgapps_config_lines += "\n"
            else:
                for pkg in app_set.package_list:
                    entry = pkg.package_title
                    nikgapps_config_lines += entry + "=" + config_dict.get(entry, "0") + "\n"
        for app_set in self.package_manager.get_packages("go"):
            if len(app_set.package_list) > 1:
                nikgapps_config_lines += "\n# Set " + app_set.title + "=0 if you want to skip installing all " \
                                                                      "packages belonging to " \
                                                                      "" + app_set.title + " Package\n"
                nikgapps_config_lines += app_set.title + "=" + config_dict.get(app_set.title, "0") + "\n\n"
                nikgapps_config_lines += "# Setting CoreGo=0 will not skip following packages," \
                                         " set them to 0 if you want to skip them  \n"
            else:
                nikgapps_config_lines += app_set.title + "=" + config_dict.get(app_set.title, "0") + "\n"
        nikgapps_config_lines += "\n"
        nikgapps_config_lines += "# Following are the Addon packages NikGapps supports\n"
        for app_set in self.package_manager.get_packages("addons"):
            nikgapps_config_lines += app_set.title + "=" + config_dict.get(app_set.title, "0") + "\n"
        if for_release:
            nikgapps_config_lines += "\n"
            nikgapps_config_lines += "# NikGapps debloater starts here, add all the stuff to add to debloater.config below (for elite and user builds only), check examples below\n"
            nikgapps_config_lines += "# YouTube\n"
            nikgapps_config_lines += "# /system/app/YouTube\n"
            nikgapps_config_lines += "\n"
        return nikgapps_config_lines

    def get_debloater_list(self):
        lines = []
        start_reading = False
        for line in self.raw_config.splitlines():
            if not start_reading and not line.__contains__("NikGapps debloater starts here"):
                continue
            start_reading = True
            if line.__eq__('') or line.__eq__('\n') or line.startswith('#') or line.__contains__("="):
                continue
            lines.append(line.replace('\n', '').strip())
        return lines

    def describe_nikgapps_config(self, get_list=False):
        list_of_apps = []
        if len(self.config_package_list) == 0:
            return "No packages are enabled to be installed." if not get_list else list_of_apps
        result = "Following Apps will be installed:\n"
        for appset in self.config_package_list:
            appset: AppSet
            result += f"\n-> {appset.title}  "
            list_of_apps.append(f"-> {appset.title}")
            if len(appset.package_list) >= 1:
                result += "\n"
                for package in appset.package_list:
                    result += f"- {package.package_title}  \n"
                    list_of_apps.append(f"- {package.package_title}")
        return result.strip() if not get_list else list_of_apps

    def upload_nikgapps_config(self):
        analytics_dict = {}
        key = "config_version_" + Statics.get_android_code(self.android_version)
        analytics_dict[key] = str(self.config_version)
        tracker_repo = GitOperations.setup_tracker_repo()
        repo_dir = tracker_repo.working_tree_dir
        if FileOp.dir_exists(repo_dir):
            print(f"{repo_dir} exists!")
            config_version_json = repo_dir + Statics.dir_sep + "config_version.json"
            if FileOp.file_exists(config_version_json):
                print("File Exists!")
                custom_builds_json_string = ""
                for line in FileOp.read_string_file(config_version_json):
                    custom_builds_json_string += line
                print(custom_builds_json_string)
                print()
                decoded_hand = json.loads(custom_builds_json_string)
                if decoded_hand.get(key) is not None:
                    version_on_server = decoded_hand[key]
                    print("version on server is: " + version_on_server)
                    if int(version_on_server) < int(self.config_version):
                        print("server needs updating")
                        if self.upload():
                            decoded_hand[key] = str(self.config_version)
                            with open(config_version_json, "w") as file:
                                json.dump(decoded_hand, file, indent=2)
                        else:
                            print("Cannot update the tracker since config file failed to upload")
                    elif int(version_on_server) == int(self.config_version):
                        print("server is in sync")
                    else:
                        print("server is on higher version")
                else:
                    print(f"{key} key doesn't exist! creating the file with the key")
                    if self.upload():
                        decoded_hand[key] = str(self.config_version)
                        with open(config_version_json, 'w') as f:
                            json.dump(decoded_hand, f, indent=2)
                            print(f"{config_version_json} file is created")
                    else:
                        print("Cannot update the tracker since config file failed to upload")

            else:
                print(config_version_json + " doesn't exist! creating the file")
                if self.upload():
                    with open(config_version_json, 'w') as f:
                        json.dump(analytics_dict, f, indent=2)
                        print(f"{config_version_json} file is created")
                else:
                    print("Cannot update the tracker since config file failed to upload")
            if tracker_repo.due_changes():
                print("Updating the config version to v" + str(self.config_version))
                tracker_repo.git_push("Updating config version to v" + str(self.config_version),
                                      push_untracked_files=True)
            else:
                print("There is no change in config version to update!")
        else:
            print(f"{repo_dir} doesn't exist!")

    def upload(self):
        execution_status = False
        # create nikgapps.config file and upload to sourceforge
        temp_nikgapps_config_location = Statics.get_temp_packages_directory(
            self.android_version) + Statics.dir_sep + "nikgapps.config"
        FileOp.write_string_in_lf_file(self.get_nikgapps_config(for_release=True), temp_nikgapps_config_location)
        if FileOp.file_exists(temp_nikgapps_config_location):
            release_dir = "Releases/Config"
            u = Upload(android_version=self.android_version, release_type=release_dir, upload_files=Config.UPLOAD_FILES)
            file_type = "config"
            remote_directory = u.get_cd(file_type) + "/v" + str(self.config_version)
            execution_status, download_link, file_size_mb = u.upload(file_name=temp_nikgapps_config_location,
                                                                     remote_directory=remote_directory)
            u.close_connection()
        return execution_status

    def get_release_date(self):
        release_date = None
        if self.config_path is not None:
            file_contents = FileOp.read_string_file(self.config_path)
            for line in file_contents:
                if line.startswith("RELEASE_DATE="):
                    release_date = line.split("=")[1].strip()
                    break
        return release_date

    def update_with_release_date(self, release_date=None):
        if release_date is None:
            release_date = Requests.get_release_date(self.android_version, Config.RELEASE_TYPE)
        if self.config_path is not None:
            file_contents = FileOp.read_string_file(self.config_path)
            for index, line in enumerate(file_contents):
                if line.startswith("RELEASE_DATE="):
                    file_contents[index] = f"RELEASE_DATE={release_date}\n"
                    break
                if line.startswith("Version="):
                    file_contents.insert(index, f"RELEASE_DATE={release_date}\n")
                    break
            file_string = "".join(file_contents)
            FileOp.write_string_in_lf_file(file_string, self.config_path)
        else:
            print("Invalid config path!")
