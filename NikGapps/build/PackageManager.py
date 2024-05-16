import os
from pathlib import Path

from NikGapps.helper import Config
from NikGapps.helper.AppSet import AppSet
from NikGapps.helper.Cmd import Cmd
from NikGapps.helper.FileOp import FileOp
from NikGapps.helper.Package import Package
from NikGapps.helper.Statics import Statics
from NikGapps.helper.compression.Export import Export


class PackageManager:
    def __init__(self, android_version, arch="arm64"):
        self.android_version = android_version
        self.arch = arch
        self.source_directory = os.path.join(Statics.pwd, f"{android_version}_{arch}" if arch != "arm64" else f"{android_version}")
        self.packages = []
        self.cmd = Cmd()

    def initialize_packages(self, app_set_build_list):
        for app_set in app_set_build_list:
            self.process_app_set(app_set)

    def process_app_set(self, app_set):
        app_set_path = os.path.join(self.source_directory, app_set.title)
        package_list = []

        for package in app_set.package_list:
            pkg_path = os.path.join(app_set_path, package.package_title)
            pkg = self.create_package_from_directory(pkg_path, package)
            if pkg:
                package_list.append(pkg)

        if package_list:
            self.packages.append(AppSet(app_set.title, package_list))

    def create_package_from_directory(self, pkg_path, package):
        file_dict, folder_dict, install_list = {}, {}, []
        delete_files_list, delete_overlay_list = [], []
        primary_app_location, package_name, app_type = None, None, None

        overlay_android_version = f"overlays_{Statics.get_android_code(self.android_version)}"
        overlay_dir = os.path.join(Statics.pwd, overlay_android_version, f"{package.package_title}Overlay")

        if FileOp.dir_exists(overlay_dir):
            for file in Path(overlay_dir).rglob("*.apk"):
                overlay_destination = os.path.join(pkg_path, "___overlay", Path(file).name)
                FileOp.copy_file(file, overlay_destination)

        for pkg_files in Path(pkg_path).rglob("*"):
            pkg_files_path = str(pkg_files)
            if pkg_files.is_dir() or ".git" in pkg_files_path or pkg_files_path.endswith((".gitattributes", "README.md")):
                continue
            if pkg_files_path.endswith(Statics.DELETE_FILES_NAME):
                delete_files_list.extend([line.strip() for line in FileOp.read_string_file(pkg_files) if line.strip() not in package.delete_files_list])
                continue
            pkg_files_rel_path = pkg_files_path[pkg_files_path.find("___") + 3:]
            install_list.append(pkg_files_rel_path.replace("___", "/").replace("\\", "/"))
            file_dict[pkg_files.absolute()] = pkg_files_rel_path.replace("___", "/").replace("\\", "/")

            if pkg_files_rel_path.endswith((".xml", ".prop")):
                FileOp.convert_to_lf(pkg_files_path)

            if package.package_name and pkg_files_rel_path.endswith(".apk") and "split_" not in pkg_files_rel_path and "___m" not in pkg_files_rel_path and "___overlay" not in pkg_files_rel_path:
                primary_app_location = pkg_files.absolute()
                package_name = self.cmd.get_package_details(primary_app_location, "name")
                if "___priv-app___" in str(primary_app_location):
                    app_type = Statics.is_priv_app
                elif "___app___" in str(primary_app_location):
                    app_type = Statics.is_system_app

            for folder in FileOp.get_dir_list(pkg_files_rel_path):
                if folder.startswith(("system", "vendor", "product", "system_ext", "overlay")):
                    continue
                folder_dict[folder] = folder

        if not primary_app_location and not package.package_title:
            return None

        pkg = Package(package.package_title, package_name, app_type, package.package_title)
        pkg.install_list = install_list
        pkg.partition = package.partition
        pkg.clean_flash_only = package.clean_flash_only
        pkg.file_dict = file_dict
        pkg.folder_dict = folder_dict
        pkg.addon_index = package.addon_index
        pkg.additional_installer_script = package.additional_installer_script
        pkg.primary_app_location = primary_app_location

        if primary_app_location and app_type == Statics.is_priv_app:
            permissions_list = self.cmd.get_white_list_permissions(primary_app_location)
            permissions_list.extend([perm for perm in package.priv_app_permissions if perm not in permissions_list])
            if permissions_list and "Exception" not in permissions_list[0]:
                pkg.generate_priv_app_whitelist(package.package_title, permissions_list, self.android_version, self.source_directory)

        delete_files_list.extend(package.delete_files_list)
        delete_overlay_list.extend(package.delete_overlay_list)
        pkg.delete_files_list = delete_files_list
        pkg.delete_overlay_list = delete_overlay_list
        pkg.validation_script = package.validation_script
        pkg.overlay_list = package.overlay_list

        return pkg

    def filter_packages_by_config(self, config_obj):
        filtered_packages = []
        for app_set in self.packages:
            filtered_package_list = []
            for package in app_set.package_list:
                if config_obj.get_dictionary_value(package.package_title) in ("1", "2"):
                    filtered_package_list.append(package)
            if filtered_package_list:
                filtered_packages.append(AppSet(app_set.title, filtered_package_list))
        return filtered_packages

    # def create_zip(self, filtered_packages, package_name, config_obj):
    #     file_name = package_name
    #     config_obj.config_package_list = filtered_packages
    #     print(f"Exporting {file_name}")
    #     z = Export(file_name, sign=sign_zip)
    #     result = z.zip(config_obj=config_obj, send_zip_device=send_zip_device, fresh_build=fresh_build, telegram=telegram, compression_mode=Modes.DEFAULT)
    #     if result[1] and Config.UPLOAD_FILES:
    #         print(f"Uploading {result[0]}")
    #         execution_status, download_link, file_size_mb = upload.upload(result[0], telegram=telegram)
    #         print("Done")
    #         return execution_status
    #     else:
    #         print("Package List Empty!")
    #         return False
