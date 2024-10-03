import concurrent.futures
import os
from multiprocessing import cpu_count
from pathlib import Path
from threading import Lock

from NikGapps.helper import Config
from NikGapps.helper.Package import Package
from niklibrary.helper.F import F
from niklibrary.helper.Cmd import Cmd
from NikGapps.helper.AppSet import AppSet
from niklibrary.helper.Statics import Statics
from niklibrary.helper.T import T


class Build:
    project_name = "NikGapps"

    # Just provide the package list, and it will pick them up from the directory and build them for you
    @staticmethod
    def build_from_directory(app_set_build_list, android_version, cached=False):
        if cached:
            return app_set_build_list
        building = T()
        source_directory = Config.APK_SOURCE
        print(f"Building from {source_directory}")
        cmd = Cmd()
        app_set_list = []
        max_workers = cpu_count()
        lock = Lock()

        def process_package(app_set_obj, pkg_obj):
            package_title = pkg_obj.package_title
            app_set_path = os.path.join(source_directory, app_set_obj.title)
            pkg_path = os.path.join(str(app_set_path), package_title)

            print(f"Setting up {app_set_obj.title}/{package_title}")

            file_dict = {}
            folder_dict = {}
            install_list = []
            delete_files_list = []
            delete_overlay_list = []
            package_name = None
            app_type = None
            primary_app_location = None

            if float(android_version) >= 12.1:
                overlay_directory = Config.OVERLAY_SOURCE
                overlay_dir = overlay_directory + Statics.dir_sep + f"{package_title}Overlay"
                if F.dir_exists(overlay_dir):
                    for file in Path(overlay_dir).rglob("*.apk"):
                        pkg_files_path = "overlay" + Statics.dir_sep + Path(file).name
                        install_list.append(pkg_files_path.replace("___", "/"))
                        file_dict_value = str(pkg_files_path.replace("___", "/")).replace("\\", "/")
                        value = str(file_dict_value).split("/")
                        file_dict[str(file)] = "___" + "___".join(value[:len(value) - 1]) + "/" + value[len(value) - 1]

            for pkg_files in Path(pkg_path).rglob("*"):
                if Path(pkg_files).is_dir() or str(pkg_files).__contains__(".git") \
                        or str(pkg_files).endswith(".gitattributes") or str(pkg_files).endswith("README.md"):
                    continue
                if str(pkg_files).endswith(Statics.DELETE_FILES_NAME):
                    for str_data in F.read_string_file(pkg_files):
                        delete_file = str_data.strip()
                        if delete_file not in delete_files_list:
                            delete_files_list.append(delete_file)
                    continue
                pkg_files_path = str(pkg_files)
                pkg_files_path = pkg_files_path[pkg_files_path.find("___") + 3:]
                if pkg_files_path.replace("\\", "/").__eq__(f"etc___permissions/{pkg_obj.package_name}.xml"):
                    continue
                if pkg_obj.package_name is not None and str(pkg_files_path).endswith(".apk") and not str(
                        pkg_files).__contains__("split_") and not str(pkg_files).__contains__("___m") \
                        and not str(pkg_files).__contains__("___overlay"):
                    primary_app_location = pkg_files.absolute()
                    package_name = cmd.get_package_details(primary_app_location, "name")
                    if str(primary_app_location).__contains__("___priv-app___"):
                        app_type = Statics.is_priv_app
                    elif str(primary_app_location).__contains__("___app___"):
                        app_type = Statics.is_system_app
                for folder in F.get_dir_list(pkg_files_path):
                    if folder.startswith("system") or folder.startswith("vendor") \
                            or folder.startswith("product") or folder.startswith("system_ext") \
                            or folder.startswith("overlay"):
                        continue
                    folder_dict[folder] = folder
                # We don't need this but for the sake of consistency
                if str(pkg_files_path).endswith("xml") or str(pkg_files_path).endswith("prop"):
                    F.convert_to_lf(str(pkg_files.absolute()))
                install_list.append(pkg_files_path.replace("___", "/"))
                file_dict_value = str(pkg_files_path.replace("___", "/")).replace("\\", "/")
                value = str(file_dict_value).split("/")
                file_dict[pkg_files.absolute()] = "___" + "___".join(value[:len(value) - 1]) + "/" + value[
                    len(value) - 1]

            if primary_app_location is not None:
                title = os.path.basename(primary_app_location)[:-4]
            else:
                title = package_title

            # Create a new Package object with the gathered data
            pkg = Package(title, package_name, app_type, package_title)
            pkg.install_list = install_list
            pkg.partition = pkg_obj.partition
            pkg.clean_flash_only = pkg_obj.clean_flash_only
            pkg.file_dict = file_dict
            pkg.folder_dict = folder_dict
            pkg.addon_index = pkg_obj.addon_index
            pkg.additional_installer_script = pkg_obj.additional_installer_script
            pkg.primary_app_location = primary_app_location

            if pkg.primary_app_location is not None and app_type == Statics.is_priv_app:
                permissions_list = cmd.get_white_list_permissions(primary_app_location)
                for perm in pkg_obj.priv_app_permissions:
                    permissions_list.append(perm)
                if permissions_list and not permissions_list[0].__contains__("Exception"):
                    pkg.priv_app_permissions_str = pkg.generate_priv_app_whitelist(app_set_obj.title, permissions_list,
                                                                                   android_version=android_version,
                                                                                   pkg_path=source_directory)
            pkg.delete_files_list = delete_files_list
            for delete_app in pkg_obj.delete_files_list:
                pkg.delete(delete_app)
            pkg.delete_overlay_list = delete_overlay_list
            pkg.validation_script = pkg_obj.validation_script
            pkg.overlay_list = pkg_obj.overlay_list

            return pkg

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            app_set_futures = {}

            for app_set in app_set_build_list:
                futures = []
                for pkg_object in app_set.package_list:
                    future = executor.submit(process_package, app_set, pkg_object)
                    futures.append(future)
                app_set_futures[app_set.title] = futures

            for app_set_title, futures in app_set_futures.items():
                package_list = []
                for future in concurrent.futures.as_completed(futures):
                    package_list.append(future.result())

                if package_list:
                    with lock:
                        app_set_to_build = AppSet(app_set_title, package_list)
                        app_set_list.append(app_set_to_build)
        print(f"Total Time Taken: {building.taken()}")
        return app_set_list
