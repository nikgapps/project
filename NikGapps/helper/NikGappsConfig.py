import json
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

    def __init__(self, android_version, config_path=None, config_version=None, use_zip_config=None, raw_config=None,
                 arch="arm64"):
        self.config_version = Statics.config_versions[android_version]
        self.android_version = android_version
        if config_version is not None:
            self.config_version = config_version
        self.default_mode = "default"
        self.install_mode = "install"
        self.enabled_mode = 1
        self.disabled_mode = 0
        self.use_zip_config = 0
        if use_zip_config is not None:
            self.use_zip_config = use_zip_config
        self.config_objects = self.build_config_objects()
        self.config_package_list = []
        self.config_dict = None
        self.debloater_list = []
        if raw_config is not None:
            self.config_dict = self.get_config_dictionary(raw_config)
            self.debloater_list = self.get_debloater_list(raw_config)
        if config_path is not None:
            self.config_path = config_path
            self.config_dict = self.get_config_dictionary()
            self.debloater_list = self.get_debloater_list()
        if self.config_dict is not None:
            for config_obj in self.config_objects:
                if config_obj.key in self.config_dict:
                    config_obj.value = str(self.config_dict[config_obj.key])
            self.config_package_list = self.get_config_packages()
            # print("-------------------------------------------------------------------------------------")
            # print(self.describe_nikgapps_config())
            # print("-------------------------------------------------------------------------------------")
        self.exclusive = False
        self.config_string = self.get_nikgapps_config(config_dict=self.config_dict)
        self.arch = arch
        self.creator = "Nikhil Menghani"

    def build_config_objects(self, config_dict=None):
        config_list = []
        predefined_configs = {
            "AndroidVersion": self.android_version,
            "Version": self.config_version,
            "LogDirectory": {
                "value": self.default_mode,
                "description": """# set this to the directory you want to copy the logs to.
# for e.g. LogDirectory="/system/etc" will install the logs to /system/etc/nikgapps_logs directory
# by default it will install it to /sdcard/NikGapps/nikgapps_logs"""
            },
            "InstallPartition": {
                "value": self.default_mode,
                "description": "# set to /system, /product or /system_ext if you want to force the installation to aforementioned locations"
            },
            "mode": {
                "value": self.install_mode,
                "description": "# set to uninstall if you want to uninstall any google app, also set the value of google app below to -1"
            },
            "WipeDalvikCache": {
                "value": self.enabled_mode,
                "description": "# set WipeDalvikCache=0 if you don't want the installer to wipe dalvik/cache after installing the gapps"
            },
            "WipeRuntimePermissions": {
                "value": self.disabled_mode,
                "description": "# set WipeRuntimePermissions=1 if you want to wipe runtime permissions"
            },
            "execute.d": {
                "value": self.enabled_mode,
                "description": "# Addon.d config set it to 0 to skip the automatic backup/restore while flashing the rom"
            },
            "use_zip_config": {
                "value": self.use_zip_config,
                "description": "# if you want to force the installer to use the config from gapps zip file, set below to 1"
            },
            "gms_optimization": {
                "value": self.disabled_mode,
                "description": "# set this to 1 if you want to enable gms optimization, careful while doing it, you may experience issues like delayed notification with some Roms"
            }
        }
        if config_dict is not None:
            for key, value in config_dict.items():
                if key not in predefined_configs:
                    if key == "Core":
                        break
                    config = ConfigObj(key, value)
                    config_list.append(config)
        for key, config_info in predefined_configs.items():
            if isinstance(config_info, dict):
                value = config_info["value"]
                description = config_info.get("description", None)
            else:
                value = config_info
                description = None
            config = ConfigObj(key, value)
            config.description = description
            config_list.append(config)
        return config_list

    def get_config_dictionary(self, raw_config=None):
        lines = {}
        for line in FileOp.read_string_file(self.config_path) if raw_config is None else raw_config.splitlines():
            if line.__eq__('') or line.__eq__('\n') or line.startswith('#') \
                    or line.startswith("File Not Found") \
                    or line.startswith("use_zip_config=") \
                    or not line.__contains__("="):
                continue
            lines[line.split('=')[0]] = line.split('=')[1].replace('\n', '')
        return lines

    def get_debloater_list(self, raw_config=None):
        lines = []
        start_reading = False
        for line in FileOp.read_string_file(self.config_path) if raw_config is None else raw_config.splitlines():
            if not start_reading and not line.__contains__("NikGapps debloater starts here"):
                continue
            start_reading = True
            if line.__eq__('') or line.__eq__('\n') or line.startswith('#') or line.__contains__("="):
                continue
            lines.append(line.replace('\n', '').strip())
        return lines

    def get_config_packages(self):
        config_dict = self.config_dict
        # print(json.dumps(config_dict, indent=4))
        # pprint.pprint(config_dict)
        app_set_list = []
        pre_defined_addons = []
        for addons in NikGappsPackages.get_packages("addons", self.android_version):
            pre_defined_addons.append(addons.title)
        for app_set in NikGappsPackages.get_packages("all", self.android_version):
            app_set: AppSet
            if app_set.title not in config_dict:
                continue
            pkg_len = len(app_set.package_list)
            new_app_set = None
            if pkg_len > 1 and str(config_dict[app_set.title]) == "1":
                new_app_set = AppSet(app_set.title)
                for pkg in app_set.package_list:
                    pkg: Package
                    if app_set.title.lower() == "corego":
                        # corego will be added by default
                        new_app_set.add_package(pkg)
                        if pkg.package_title != "ExtraFilesGo":
                            self.config_dict[str(">>" + pkg.package_title)] = "1"
                        continue
                    if str(">>" + pkg.package_title) not in config_dict:
                        if app_set.title in pre_defined_addons:
                            # these will be the addons who can be directly added
                            new_app_set.add_package(pkg)
                        continue
                    if config_dict[str(">>" + pkg.package_title)] in ("1", "2"):
                        new_app_set.add_package(pkg)
                    else:
                        print("Package disabled " + pkg.package_title)
            elif pkg_len == 1 and str(config_dict[app_set.title]) == "1":
                new_app_set = app_set
            if new_app_set is not None:
                app_set_list.append(new_app_set)
        return app_set_list

    def get_user_name_from_config(self):
        if self.config_path is None:
            return "Anonymous"
        return str(self.config_path).split("/")[-2]

    def get_dictionary_value(self, key):
        if key in self.config_dict:
            return str(self.config_dict[key])
        return str(0)

    def get_nikgapps_config(self, config_dict=None, config_objects=None, for_release=False, override=False):
        nikgapps_config_lines = "# NikGapps configuration file\n\n"
        nikgapps_config_lines += "# If you are not sure about the config, " \
                                 "just skip making changes to it or comment it by adding # before it\n"
        nikgapps_config_lines += "# visit https://nikgapps.com/misc/2022/02/22/" \
                                 "NikGapps-Config.html to read everything about nikgapps\n\n"

        for config_obj in self.config_objects if config_objects is None else config_objects:
            nikgapps_config_lines += config_obj.get_string()

        nikgapps_config_lines += "# Following are the packages with default configuration\n"

        for app_set in NikGappsPackages.get_packages("full", self.android_version):
            if len(app_set.package_list) > 1:
                nikgapps_config_lines += "\n# Set " + app_set.title + "=0 if you want to skip installing all " \
                                                                      "packages belonging to " \
                                                                      "" + app_set.title + " Package\n"
                if config_dict is not None:
                    nikgapps_config_lines += app_set.title + "=" + self.get_dictionary_value(app_set.title) + "\n"
                    for pkg in app_set.package_list:
                        entry = ">>" + pkg.package_title
                        nikgapps_config_lines += entry + "=" + self.get_dictionary_value(entry) + "\n"
                else:
                    nikgapps_config_lines += app_set.title + "=" + ("0" if override else str(1)) + "\n"
                    for pkg in app_set.package_list:
                        nikgapps_config_lines += ">>" + pkg.package_title + "=" + (
                            "0" if override else str(pkg.enabled)) + "\n"
                nikgapps_config_lines += "\n"
            else:
                if config_dict is not None:
                    for pkg in app_set.package_list:
                        entry = pkg.package_title
                        nikgapps_config_lines += entry + "=" + self.get_dictionary_value(entry) + "\n"
                else:
                    for pkg in app_set.package_list:
                        nikgapps_config_lines += pkg.package_title + "=" + (
                            "0" if override else str(pkg.enabled)) + "\n"
        for app_set in NikGappsPackages.get_packages("go", self.android_version):
            if len(app_set.package_list) > 1:
                nikgapps_config_lines += "\n# Set " + app_set.title + "=0 if you want to skip installing all " \
                                                                        "packages belonging to " \
                                                                        "" + app_set.title + " Package\n"
                if config_dict is not None:
                    nikgapps_config_lines += app_set.title + "=" + self.get_dictionary_value(app_set.title) + "\n\n"
                else:
                    nikgapps_config_lines += app_set.title + "=" + ("0" if override else str(1)) + "\n\n"
                nikgapps_config_lines += "# Setting CoreGo=0 will not skip following packages," \
                                         " set them to 0 if you want to skip them  \n"
            else:
                if config_dict is not None:
                    nikgapps_config_lines += app_set.title + "=" + self.get_dictionary_value(app_set.title) + "\n"
                else:
                    nikgapps_config_lines += app_set.title + "=" + ("0" if override else str(1)) + "\n"
        nikgapps_config_lines += "\n"
        nikgapps_config_lines += "# Following are the Addon packages NikGapps supports\n"
        for app_set in NikGappsPackages.get_packages("addons", self.android_version):
            if config_dict is not None:
                nikgapps_config_lines += app_set.title + "=" + self.get_dictionary_value(app_set.title) + "\n"
            else:
                nikgapps_config_lines += app_set.title + "=" + ("0" if override else str(1)) + "\n"
        if for_release:
            nikgapps_config_lines += "\n"
            nikgapps_config_lines += "# NikGapps debloater starts here, add all the stuff to add to debloater.config below (for elite and user builds only), check examples below\n"
            nikgapps_config_lines += "# YouTube\n"
            nikgapps_config_lines += "# /system/app/YouTube\n"
            nikgapps_config_lines += "\n"
        return nikgapps_config_lines

    def describe_nikgapps_config(self, get_list=False):
        list_of_apps = []
        if len(self.config_package_list) == 0:
            return "No packages are enabled to be installed." if not get_list else list_of_apps
        result = "Following Apps will be installed:\n"
        for appset in self.config_package_list:
            appset: AppSet
            result += f"\n-> {appset.title}  "
            list_of_apps.append(f"-> {appset.title}")
            if len(appset.package_list) > 1:
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
            execution_status, download_link, file_size_mb = u.upload(file_name=temp_nikgapps_config_location, remote_directory=remote_directory)
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

    def upgrade_config(self):
        standard_dict = self.get_config_dictionary(
            self.get_nikgapps_config(config_objects=self.build_config_objects(), for_release=True, override=True))
        for key in standard_dict.keys():
            if self.config_dict.get(key) is None:
                self.config_dict[key] = standard_dict[key]
        self.config_dict["Version"] = self.config_version
        self.config_dict["use_zip_config"] = 1
        self.config_objects = self.build_config_objects(self.config_dict)
        self.config_package_list = self.get_config_packages()
        self.config_string = self.get_nikgapps_config(config_dict=self.config_dict, config_objects=self.config_objects,
                                                      for_release=True)
        for debloat in self.debloater_list:
            self.config_string += debloat + "\n"
