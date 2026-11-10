import concurrent.futures
import os
from multiprocessing import cpu_count
from pathlib import Path
from threading import Lock

from NikGapps.helper import Config
from NikGapps.helper.Package import Package
from niklibrary.helper.F import F
from NikGapps.helper.AppSet import AppSet
from niklibrary.helper.Statics import Statics
from niklibrary.helper.T import T
from NikGapps.build.GoSupport import core_source_appset, generated_go_files
from nikgapps_package_pipeline.apk import Aapt2Inspector, find_aapt2
from NikGapps.build.Requirements import required_overlays


class Build:
    project_name = "NikGapps"

    # Just provide the package list, and it will pick them up from the directory and build them for you
    @staticmethod
    def build_from_directory(app_set_build_list, android_version, cached=False):
        if cached:
            return app_set_build_list
        building = T()
        if Config.PACKAGE_SOURCE == "registry":
            print("[Registry] Package source mode is enabled; skipping the legacy APK repository")
            from nikgapps_package_pipeline.consumer import (
                CatalogPackageSource,
                channel_overrides_from_env,
            )
            registry_source = CatalogPackageSource(
                Config.PACKAGE_CATALOG_URL,
                Config.PACKAGE_APPSETS_URL,
                Path(Config.PACKAGE_CACHE),
                channel=Config.PACKAGE_CHANNEL,
                channel_overrides=channel_overrides_from_env(Config.PACKAGE_CHANNEL_OVERRIDES),
                release_index_url=Config.PACKAGE_RELEASE_INDEX_URL,
                release_id=Config.PACKAGE_RELEASE_ID,
                token=os.environ.get("GITLAB_TOKEN"),
            )
            Config.APK_SOURCE = str(registry_source.prepare(
                app_set_build_list,
                android_version,
                getattr(Config, "PACKAGE_ARCH", "arm64"),
            ))
            print(f"[Registry] Handing prepared source to the existing builder: {Config.APK_SOURCE}")
            print("[Registry] Final NikGapps ZIP assembly remains unchanged")
            if Config.OVERLAY_SOURCE is None:
                overlay_path = Path(Config.APK_SOURCE) / ".overlays"
                overlay_path.mkdir(parents=True, exist_ok=True)
                Config.OVERLAY_SOURCE = str(overlay_path)
        source_directory = Config.APK_SOURCE
        print(f"Building from {source_directory}")
        inspector = Aapt2Inspector(Config.AAPT2 or find_aapt2())
        app_set_list = []
        max_workers = cpu_count()
        lock = Lock()

        def process_package(app_set_obj, pkg_obj):
            package_title = pkg_obj.package_title
            source_appset = (core_source_appset(app_set_obj.title, package_title, android_version)
                             if Config.PACKAGE_SOURCE != "registry" else app_set_obj.title)
            app_set_path = os.path.join(source_directory, source_appset)
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

            source_files = list(Path(pkg_path).rglob("*"))
            if float(android_version) >= 17 and app_set_obj.title == "CoreGo" and package_title == "GmsCore" and Config.PACKAGE_SOURCE != "registry":
                generated = generated_go_files(Path(pkg_path), Path(Statics.get_temp_packages_directory(android_version)) / "go-source")
                source_files = [path for path in source_files if path.relative_to(pkg_path).as_posix() not in generated]
                source_files.extend(generated.values())
            # Registry sources carry overlays inside the package; raw sources
            # add them above. Keep the same install/uninstall order in both modes.
            def source_order(path):
                name = path.as_posix()
                name = name[name.find("___"):]
                return (not name.startswith("___overlay/"), name)
            source_files.sort(key=source_order)
            for pkg_files in source_files:
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
                    package_name = inspector.inspect(primary_app_location).package_name
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
                install_list.append(pkg_files_path.replace("___", "/"))
                file_dict_value = str(pkg_files_path.replace("___", "/")).replace("\\", "/")
                value = str(file_dict_value).split("/")
                file_dict[pkg_files.absolute()] = "___" + "___".join(value[:len(value) - 1]) + "/" + value[
                    len(value) - 1]

            if primary_app_location is not None:
                title = os.path.basename(primary_app_location)[:-4]
            else:
                title = package_title

            overlays_present = {Path(value).name for value in file_dict.values() if value.startswith('___overlay/')}
            missing_overlays = required_overlays(package_title, android_version) - overlays_present
            if missing_overlays:
                raise ValueError(f'{app_set_obj.title}/{package_title}: missing required overlays: {sorted(missing_overlays)}')

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
                permissions_list = inspector.privileged_permissions(primary_app_location)
                for perm in pkg_obj.priv_app_permissions:
                    permissions_list.append(perm)
                if permissions_list:
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
