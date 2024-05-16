import os
from NikGapps.build.Build import Build
from NikGapps.build.PackageManager import PackageManager
from NikGapps.helper import Config
from NikGapps.helper.NikGappsConfig import NikGappsConfig
from NikGapps.helper.Statics import Statics
from NikGapps.helper.T import T
from NikGapps.helper.compression.Modes import Modes
from NikGapps.build.NikGappsPackages import NikGappsPackages
from NikGapps.helper.compression.Export import Export


class Release:

    @staticmethod
    def zip(build_package_list, android_version, arch, sign_zip, send_zip_device, fresh_build, telegram, upload=None):
        release_directory = Statics.get_release_directory(android_version)
        current_time = T.get_current_time()

        # def zip_package1(package_name, app_set_list, config_obj=None):
        #     package_manager = PackageManager(android_version, arch)
        #     package_manager.initialize_packages(app_set_list)
        #
        #     if config_obj is None:
        #         config_obj = NikGappsConfig(android_version=android_version, arch=arch)
        #     else:
        #         if config_obj.config_package_list:
        #             app_set_list = config_obj.config_package_list
        #
        #     filtered_packages = package_manager.filter_packages_by_config(config_obj)
        #
        #     return package_manager.create_zip(filtered_packages, package_name, config_obj)

        def zip_package(package_name, app_set_list, config_obj=None):
            if config_obj is None:
                config_obj = NikGappsConfig(android_version=android_version, arch=arch)
            else:
                if config_obj.config_package_list:
                    app_set_list = config_obj.config_package_list

            if app_set_list:
                file_name = package_name
                config_obj.config_package_list = Build.build_from_directory(app_set_list, android_version, arch)
                print(f"Exporting {file_name}")
                z = Export(file_name, sign=sign_zip)
                result = z.zip(config_obj=config_obj, send_zip_device=send_zip_device, fresh_build=fresh_build,
                               telegram=telegram, compression_mode=Modes.DEFAULT)
                if result[1] and Config.UPLOAD_FILES:
                    print(f"Uploading {result[0]}")
                    execution_status, download_link, file_size_mb = upload.upload(result[0], telegram=telegram)
                    print("Done")
                    return execution_status
            else:
                print("Package List Empty!")
                return False

        def handle_addons(package_type_inner):
            for app_set in NikGappsPackages.get_packages(package_type_inner, android_version):
                print(f"Building for {app_set.title}")
                package_name = f"{release_directory}{Statics.dir_sep}addons{Statics.dir_sep}NikGapps-Addon-{android_version}-{app_set.title}-{current_time}.zip"
                zip_package(package_name, [app_set])

        def handle_special_case(special_case_type):
            file_name = f"{release_directory}{Statics.dir_sep}{special_case_type.capitalize()}-{current_time}.zip"
            z = Export(file_name=file_name, sign=sign_zip)
            config_obj = NikGappsConfig(android_version=android_version)
            zip_result = z.zip(config_obj=config_obj, send_zip_device=send_zip_device, fresh_build=fresh_build,
                               telegram=telegram, compression_mode=Modes.DEFAULT)
            if zip_result[1] and Config.UPLOAD_FILES:
                print(f"Uploading {zip_result[0]}")
                execution_status, download_link, file_size_mb = upload.upload(zip_result[0], telegram=telegram)
                print("Done")
                return execution_status
            else:
                print("Failed to create zip!")

        def handle_build_package(package_type_inner):
            file_name = f"{release_directory}{Statics.dir_sep}{T.get_file_name(package_type_inner.lower(), android_version, arch)}"
            print(f"Building for {package_type_inner}")
            zip_package(file_name, NikGappsPackages.get_packages(package_type_inner, android_version))

        def handle_default(default_type):
            for app_set in NikGappsPackages.get_packages(default_type, android_version):
                if app_set is None:
                    print(f"AppSet/Package Does not Exist: {default_type}")
                else:
                    print(f"Building for {app_set.title}")
                    package_name = f"{release_directory}{Statics.dir_sep}addons{Statics.dir_sep}NikGapps-Addon-{android_version}-{app_set.title}-{current_time}.zip"
                    zip_package(package_name, [app_set])

        for pkg_type_outer in build_package_list:
            print(f"Currently Working on {pkg_type_outer}")
            os.environ['pkg_type'] = str(pkg_type_outer)

            if "addons" in str(pkg_type_outer).lower():
                handle_addons(pkg_type_outer)
            elif str(pkg_type_outer).lower() in ["debloater", "removeotascripts"]:
                special_case_result = handle_special_case(pkg_type_outer)
                if special_case_result:
                    return special_case_result
            elif pkg_type_outer in Config.BUILD_PACKAGE_LIST:
                handle_build_package(pkg_type_outer)
            else:
                handle_default(pkg_type_outer)

            os.environ['pkg_type'] = ''
