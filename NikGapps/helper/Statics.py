import math
import os
from pathlib import Path
from .T import T


class Statics:
    time = T.get_london_date_time("%y%m%d%H%M")
    android_versions = {
        '10': {'sdk': '29', 'code': 'Q'},
        '11': {'sdk': '30', 'code': 'R'},
        '12': {'sdk': '31', 'code': 'S'},
        '12.1': {'sdk': '32', 'code': 'SL'},
        '13': {'sdk': '33', 'code': 'T'}
    }
    config_versions = {
        '10': '30',
        '11': '30',
        '12': '30',
        '12.1': '30',
        '13': '30'
    }
    is_system_app = 1
    is_priv_app = 2
    system_root_dir = "/system/product"
    cwd = os.getcwd()
    pwd = str(Path(cwd).parent)
    dir_sep = os.path.sep
    release_directory = cwd + dir_sep + "Releases"
    DELETE_FILES_NAME = "DeleteFilesData"
    meta_inf_dir = "META-INF/com/google/android/"
    nikgapps_config = "nikgapps.config"
    release_tracker_url = "https://raw.githubusercontent.com/nikgapps/tracker/main/release_tracker.json"
    folder_access_url = "https://raw.githubusercontent.com/nikgapps/tracker/main/folder_access.json"
    admin_access_url = "https://raw.githubusercontent.com/nikgapps/tracker/main/admin_access.txt"
    admin_access = None
    folder_access = None

    @staticmethod
    def get_import_path(app_set, pkg, install_path, target_version, export_directory=None):
        base_name = os.path.basename(install_path)
        dir_name = Statics.get_parent_path(install_path)
        dir_name = str(dir_name).replace("\\system_ext", "").replace("/system_ext", "") \
            .replace("\\system", "").replace("/system", "") \
            .replace("\\product", "").replace("/product", "")
        if export_directory is not None:
            output = export_directory + os.path.sep
        else:
            output = Statics.cwd + os.path.sep + "Export" + os.path.sep + str(
                target_version) + os.path.sep + T.get_london_date_time("%Y%m%d") + os.path.sep
        if app_set is not None:
            output += app_set + os.path.sep
        output += str(pkg) + os.path.sep + str(dir_name).replace("\\", "___").replace(
            os.path.sep, "___") + os.path.sep + base_name
        if not os.path.exists(Path(output).parent):
            os.makedirs(Path(output).parent)
        return Path(output)

    @staticmethod
    def get_parent_path(file_path):
        return Path(file_path).parent

    @staticmethod
    def get_download_link(file_name, sf_path):
        sf_prefix = "https://sourceforge.net/projects/nikgapps/files/"
        download_link = sf_prefix + sf_path[len("/home/frs/project/nikgapps/"):] + "/" + os.path.basename(
            file_name) + "/download"
        return download_link

    @staticmethod
    def get_file_bytes(file_name):
        file_stats = os.stat(file_name)
        # 1000 instead of 1024 because it's better to require more size than what gapps exactly takes
        return math.ceil(file_stats.st_size / 1000)

    @staticmethod
    def get_temp_packages_directory(android_version, arch="arm64"):
        return Statics.cwd + os.path.sep + "TempPackages" + os.path.sep + str(android_version) + os.path.sep + arch

    @staticmethod
    def get_overlay_source_directory(android_version):
        return Statics.cwd + os.path.sep + f"overlays_{Statics.get_android_code(android_version)}_source"

    @staticmethod
    def get_overlay_source_repo(android_version):
        return f"git@github.com:nikgapps/overlays_{Statics.get_android_code(android_version)}_source.git"

    @staticmethod
    def get_overlay_directory(android_version):
        return Statics.cwd + os.path.sep + f"overlays_{Statics.get_android_code(android_version)}"

    @staticmethod
    def get_overlay_repo(android_version):
        return f"git@github.com:nikgapps/overlays_{Statics.get_android_code(android_version)}.git"

    @staticmethod
    def get_temp_overlay_directory(android_version):
        return Statics.get_temp_packages_directory(android_version) + os.path.sep + "Overlays"

    @staticmethod
    def get_release_directory(android_version):
        return Statics.release_directory + os.path.sep + str(android_version)

    @staticmethod
    def get_android_code(android_version):
        return Statics.android_versions[str(android_version)]['code']

    @staticmethod
    def get_android_sdk(android_version):
        return Statics.android_versions[str(android_version)]['sdk']

    @staticmethod
    def get_sourceforge_release_directory(release_dir):
        sourceforge_root_directory = "/home/frs/project/nikgapps"
        match release_dir:
            case ("config"):
                return f"{sourceforge_root_directory}/Config-Releases"
            case ("canary"):
                return f"{sourceforge_root_directory}/Canary-Releases"
            case ("stable"):
                return f"{sourceforge_root_directory}/Releases"
            case _:
                return f"{sourceforge_root_directory}/{release_dir}"

    @staticmethod
    def get_partition(android_version, partition):
        if float(android_version) <= 10:
            return "product"
        return partition
