import json
import os

from . import Config
from .ConfigObj import ConfigObj
from .FileOp import FileOp
from .AppSet import AppSet
from .Package import Package
from NikGapps.build.NikGappsPackages import NikGappsPackages
from .Statics import Statics
from .git.GitOperations import GitOperations
from .web.Requests import Requests
from NikGapps.helper.upload.Upload import Upload


class NikGappsConfig:

    def __init__(self, android_version: str, config_path: str = None, config_version: int = None,
                 use_zip_config: int = None, raw_config: str = None, arch: str = "arm64"):
        self.android_version = android_version
        self.config_version = config_version if config_version is not None else Statics.config_versions[android_version]
        self.use_zip_config = use_zip_config if use_zip_config is not None else 0
        self.config_path = config_path
        self.arch = arch
        self.default_mode = "default"
        self.install_mode = "install"
        self.enabled_mode = 1
        self.disabled_mode = 0
        self.config_objects = self.build_config_objects()
        self.config_package_list = []
        self.config_dict = None
        self.debloater_list = []
        if raw_config:
            self.config_dict = self.get_config_dictionary(raw_config)
            self.debloater_list = self.get_debloater_list(raw_config)
        elif config_path:
            self.config_dict = self.get_config_dictionary()
            self.debloater_list = self.get_debloater_list()
        if self.config_dict:
            self.load_config_objects()
            self.config_package_list = self.get_config_packages()
        self.exclusive = False
        self.config_string = self.get_nikgapps_config(self.config_dict)
        self.creator = "Nikhil Menghani"

    def build_config_objects(self, config_dict: dict = None) -> list:
        config_list = []
        predefined_configs = self.get_predefined_configs()
        if config_dict:
            for key, value in config_dict.items():
                if key not in predefined_configs:
                    if key == "Core":
                        break
                    config = ConfigObj(key, value)
                    config_list.append(config)
        config_list.extend(self.create_predefined_config_objects(predefined_configs))
        return config_list

    def get_predefined_configs(self) -> dict:
        return {
            "AndroidVersion": self.android_version,
            "Version": self.config_version,
            "LogDirectory": {"value": self.default_mode, "description": """# set this to the directory you want to copy the logs to.
# for e.g. LogDirectory="/system/etc" will install the logs to /system/etc/nikgapps_logs directory
# by default it will install it to /sdcard/NikGapps/nikgapps_logs""" },
            "InstallPartition": {"value": self.default_mode, "description": "# set to /system, /product or /system_ext if you want to force the installation to aforementioned locations" },
            "Mode": {"value": self.install_mode, "description": "# set to uninstall if you want to uninstall any google app, also set the value of google app below to -1" },
            "WipeDalvikCache": {"value": self.enabled_mode, "description": "# set WipeDalvikCache=0 if you don't want the installer to wipe dalvik/cache after installing the gapps" },
            "WipeRuntimePermissions": {"value": self.disabled_mode, "description": "# set WipeRuntimePermissions=1 if you want to wipe runtime permissions" },
            "ExecuteBackupRestore": {"value": self.enabled_mode, "description": "# Addon.d config, set it to 0 to skip the automatic backup/restore while flashing the rom" },
            "UseZipConfig": {"value": self.use_zip_config, "description": "# if you want to force the installer to use the config from gapps zip file, set below to 1" },
            "OverwriteWithZipConfig": {"value": self.disabled_mode, "description": "# if you want to overwrite the config located in /sdcard/NikGapps with gapps zip file, set below to 1. Applicable to decrypted storage only" },
            "GmsOptimization": {"value": self.disabled_mode, "description": "# set this to 1 if you want to enable gms optimization, careful while doing it, you may experience issues like delayed notification with some Roms" },
            "GenerateLogs": {"value": self.enabled_mode, "description": "# set this to 0 if you want to skip generating nikgapps logs, if you run into issues, enable it and flash the zip again to get the logs" }
        }

    def create_predefined_config_objects(self, predefined_configs: dict) -> list:
        config_list = []
        for key, config_info in predefined_configs.items():
            if isinstance(config_info, dict):
                value = config_info["value"]
                description = config_info.get("description")
            else:
                value = config_info
                description = None
            config = ConfigObj(key, value)
            config.description = description
            config_list.append(config)
        return config_list

    def load_config_objects(self):
        for config_obj in self.config_objects:
            if config_obj.key in self.config_dict:
                config_obj.value = str(self.config_dict[config_obj.key])

    def get_config_dictionary(self, raw_config: str = None) -> dict:
        lines = {}
        config_lines = FileOp.read_string_file(self.config_path) if raw_config is None else raw_config.splitlines()
        for line in config_lines:
            if line and not line.startswith(('#', 'File Not Found', 'UseZipConfig=')) and '=' in line:
                key, value = line.split('=', 1)
                lines[key] = value.strip()
        return lines

    def get_debloater_list(self, raw_config: str = None) -> list:
        lines = []
        start_reading = False
        config_lines = FileOp.read_string_file(self.config_path) if raw_config is None else raw_config.splitlines()
        for line in config_lines:
            if not start_reading and "NikGapps debloater starts here" not in line:
                continue
            start_reading = True
            if line and not line.startswith('#'):
                lines.append(line.strip())
        return lines

    def get_config_packages(self) -> list:
        config_dict = self.config_dict
        app_set_list = []
        pre_defined_addons = [addons.title for addons in NikGappsPackages.get_packages("addons", self.android_version)]
        for app_set in NikGappsPackages.get_packages("all", self.android_version):
            if app_set.title not in config_dict:
                continue
            pkg_len = len(app_set.package_list)
            new_app_set = None
            if pkg_len > 1 and str(config_dict[app_set.title]) == "1":
                new_app_set = AppSet(app_set.title)
                for pkg in app_set.package_list:
                    if app_set.title.lower() == "corego":
                        new_app_set.add_package(pkg)
                        if pkg.package_title != "ExtraFilesGo":
                            self.config_dict[f">>{pkg.package_title}"] = "1"
                        continue
                    if f">>{pkg.package_title}" not in config_dict:
                        if app_set.title in pre_defined_addons:
                            new_app_set.add_package(pkg)
                        continue
                    if config_dict[f">>{pkg.package_title}"] in ("1", "2"):
                        new_app_set.add_package(pkg)
                    else:
                        print(f"Package disabled {pkg.package_title}")
            elif pkg_len == 1 and str(config_dict[app_set.title]) in ("1", "2"):
                new_app_set = app_set
            if new_app_set:
                app_set_list.append(new_app_set)
        return app_set_list

    def get_user_name_from_config(self) -> str:
        if self.config_path is None:
            return "Anonymous"
        return str(self.config_path).split(Statics.dir_sep)[-2]

    def get_dictionary_value(self, key: str) -> str:
        return str(self.config_dict.get(key, 0))

    def get_nikgapps_config(self, config_dict: dict = None, config_objects: list = None,
                            for_release: bool = False, override: bool = False) -> str:
        lines = [
            "# NikGapps configuration file\n",
            "# If you are not sure about the config, just skip making changes to it or comment it by adding # before it\n",
            "# visit https://nikgapps.com/misc/2022/02/22/NikGapps-Config.html to read everything about nikgapps\n\n"
        ]
        config_objects = config_objects if config_objects is not None else self.config_objects
        for config_obj in config_objects:
            lines.append(config_obj.get_string())

        lines.append("# Following are the packages with default configuration\n")

        def append_package_config(app_set, title_prefix=""):
            if len(app_set.package_list) > 1:
                lines.append(f"\n# Set {app_set.title}=0 if you want to skip installing all packages belonging to {app_set.title} Package\n")
                if config_dict:
                    lines.append(f"{app_set.title}={self.get_dictionary_value(app_set.title)}\n")
                    for pkg in app_set.package_list:
                        entry = f"{title_prefix}{pkg.package_title}"
                        lines.append(f"{entry}={self.get_dictionary_value(entry)}\n")
                else:
                    lines.append(f"{app_set.title}={'0' if override else '1'}\n")
                    for pkg in app_set.package_list:
                        lines.append(f"{title_prefix}{pkg.package_title}={'0' if override else str(pkg.enabled)}\n")
            else:
                for pkg in app_set.package_list:
                    entry = pkg.package_title if not title_prefix else f"{title_prefix}{pkg.package_title}"
                    lines.append(f"{entry}={self.get_dictionary_value(entry) if config_dict else '0' if override else str(pkg.enabled)}\n")

        for app_set in NikGappsPackages.get_packages("full", self.android_version):
            append_package_config(app_set, ">>")

        for app_set in NikGappsPackages.get_packages("go", self.android_version):
            append_package_config(app_set)
            if len(app_set.package_list) > 1:
                lines.append("# Setting CoreGo=0 will not skip the following packages, set them to 0 if you want to skip them\n")

        lines.append("\n# Following are the Addon packages NikGapps supports\n")
        for app_set in NikGappsPackages.get_packages("addons", self.android_version):
            append_package_config(app_set)

        if for_release:
            lines.extend([
                "\n# NikGapps debloater starts here, add all the stuff to add to debloater.config below (for elite and user builds only), check examples below\n",
                "# YouTube\n",
                "# /system/app/YouTube\n\n"
            ])
        return "".join(lines)

    def describe_nikgapps_config(self, get_list: bool = False) -> str:
        if not self.config_package_list:
            return "No packages are enabled to be installed." if not get_list else []
        result = "Following Apps will be installed:\n"
        list_of_apps = []
        for appset in self.config_package_list:
            result += f"\n-> {appset.title}  "
            list_of_apps.append(f"-> {appset.title}")
            if appset.package_list:
                result += "\n" + "".join(f"- {package.package_title}\n" for package in appset.package_list)
                list_of_apps.extend(f"- {package.package_title}" for package in appset.package_list)
        return result.strip() if not get_list else list_of_apps

    def upload_nikgapps_config(self):
        analytics_dict = {f"config_version_{Statics.get_android_code(self.android_version)}": str(self.config_version)}
        tracker_repo = GitOperations.setup_tracker_repo()
        repo_dir = tracker_repo.working_tree_dir

        if FileOp.dir_exists(repo_dir):
            config_version_json = os.path.join(repo_dir, "config_version.json")
            if FileOp.file_exists(config_version_json):
                with open(config_version_json, "r") as file:
                    decoded_hand = json.load(file)
                version_on_server = decoded_hand.get(analytics_dict.keys()[0])
                if version_on_server is None or int(version_on_server) < int(self.config_version):
                    if self.upload():
                        decoded_hand.update(analytics_dict)
                        with open(config_version_json, "w") as file:
                            json.dump(decoded_hand, file, indent=2)
            else:
                if self.upload():
                    with open(config_version_json, "w") as file:
                        json.dump(analytics_dict, file, indent=2)
            if tracker_repo.due_changes():
                tracker_repo.git_push(f"Updating config version to v{self.config_version}", push_untracked_files=True)
        else:
            print(f"{repo_dir} doesn't exist!")

    def upload(self) -> bool:
        temp_nikgapps_config_location = os.path.join(Statics.get_temp_packages_directory(self.android_version), "nikgapps.config")
        FileOp.write_string_in_lf_file(self.get_nikgapps_config(for_release=True), temp_nikgapps_config_location)
        if FileOp.file_exists(temp_nikgapps_config_location):
            u = Upload(android_version=self.android_version, release_type="Releases/Config", upload_files=Config.UPLOAD_FILES)
            remote_directory = os.path.join(u.get_cd("config"), f"v{self.config_version}")
            execution_status, download_link, file_size_mb = u.upload(file_name=temp_nikgapps_config_location, remote_directory=remote_directory)
            u.close_connection()
            return execution_status
        return False

    def get_release_date(self):
        if self.config_path:
            for line in FileOp.read_string_file(self.config_path):
                if line.startswith("RELEASE_DATE="):
                    return line.split("=", 1)[1].strip()
        return None

    def update_with_release_date(self, release_date: str = None):
        release_date = release_date or Requests.get_release_date(self.android_version, Config.RELEASE_TYPE)
        if self.config_path:
            file_contents = FileOp.read_string_file(self.config_path)
            for index, line in enumerate(file_contents):
                if line.startswith("RELEASE_DATE="):
                    file_contents[index] = f"RELEASE_DATE={release_date}\n"
                    break
                if line.startswith("Version="):
                    file_contents.insert(index, f"RELEASE_DATE={release_date}\n")
                    break
            FileOp.write_string_in_lf_file("".join(file_contents), self.config_path)
        else:
            print("Invalid config path!")

    def upgrade_config(self):
        standard_dict = self.get_config_dictionary(self.get_nikgapps_config(config_objects=self.build_config_objects(), for_release=True, override=True))
        self.config_dict.update({key: standard_dict[key] for key in standard_dict if key not in self.config_dict})
        self.config_dict["Version"] = self.config_version
        self.config_dict["UseZipConfig"] = 1
        self.config_objects = self.build_config_objects(self.config_dict)
        self.config_package_list = self.get_config_packages()
        self.config_string = self.get_nikgapps_config(config_dict=self.config_dict, config_objects=self.config_objects, for_release=True)
        for debloat in self.debloater_list:
            self.config_string += debloat + "\n"
