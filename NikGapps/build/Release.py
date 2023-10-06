import os
from NikGapps.build.Build import Build
from NikGapps.helper import Config
from NikGapps.helper.NikGappsConfig import NikGappsConfig
from NikGapps.helper.Statics import Statics
from NikGapps.helper.T import T
from NikGapps.helper.compression.Modes import Modes
from NikGapps.helper.upload.Upload import Upload
from NikGapps.build.NikGappsPackages import NikGappsPackages
from NikGapps.helper.compression.Export import Export
from NikGapps.helper.Cmd import Cmd
from NikGapps.helper.AppSet import AppSet
from NikGapps.helper.Package import Package


class Release:
    @staticmethod
    def zip(build_package_list, android_version, arch, sign_zip, send_zip_device, fresh_build, telegram,
            upload: Upload = None):
        release_directory = Statics.get_release_directory(android_version)
        for pkg_type in build_package_list:
            print("Currently Working on " + pkg_type)
            os.environ['pkg_type'] = str(pkg_type)
            if str(pkg_type).__contains__("addons"):
                for app_set in NikGappsPackages.get_packages(pkg_type, android_version):
                    print("Building for " + str(app_set.title))
                    package_name = release_directory + Statics.dir_sep + str(
                        "addons") + Statics.dir_sep + "NikGapps-Addon-" + str(
                        android_version) + "-" + app_set.title + "-" + str(
                        T.get_current_time()) + ".zip"
                    Release.zip_package(package_name, [app_set], android_version, sign_zip, send_zip_device,
                                        fresh_build, telegram, upload=upload)
            elif str(pkg_type).lower() == "debloater" or str(pkg_type).lower() == "removeotascripts":
                file_name = release_directory + Statics.dir_sep + f"{pkg_type}-" + str(
                    T.get_current_time()) + ".zip"
                z = Export(file_name)
                config_obj = NikGappsConfig(android_version=android_version)
                result = z.zip(config_obj=config_obj, sign_zip=sign_zip, send_zip_device=send_zip_device,
                               fresh_build=fresh_build, telegram=telegram, compression_mode=Modes.DEFAULT)
                if result[1]:
                    if Config.UPLOAD_FILES:
                        print("Uploading " + str(result[0]))
                        execution_status, download_link, file_size_mb = upload.upload(result[0], telegram=telegram)
                        print("Done")
                        return execution_status
                else:
                    print("Failed to create zip!")
            else:
                if pkg_type in Config.BUILD_PACKAGE_LIST:
                    file_name = release_directory
                    file_name = file_name + Statics.dir_sep + T.get_file_name(pkg_type.lower(), android_version, arch)
                    # Build the packages from the directory
                    print("Building for " + str(pkg_type))
                    Release.zip_package(file_name,
                                        NikGappsPackages.get_packages(pkg_type, android_version), android_version,
                                        sign_zip, send_zip_device, fresh_build, telegram, arch=arch, upload=upload)
                else:
                    for app_set in NikGappsPackages.get_packages(pkg_type, android_version):
                        if app_set is None:
                            print("AppSet/Package Does not Exists: " + str(pkg_type))
                        else:
                            print("Building for " + str(app_set.title))
                            package_name = f"{release_directory}{Statics.dir_sep}addons" \
                                           f"{Statics.dir_sep}NikGapps-Addon-{str(android_version)}-" \
                                           f"{app_set.title}-{str(T.get_current_time())}.zip"
                            Release.zip_package(package_name, [app_set], android_version, sign_zip, send_zip_device,
                                                fresh_build, telegram, upload=upload)
            os.environ['pkg_type'] = ''

    @staticmethod
    def zip_package(package_name, app_set_list, android_version, sign_zip, send_zip_device, fresh_build, telegram,
                    arch="arm64",
                    config_obj: NikGappsConfig = None,
                    upload: Upload = None):
        if config_obj is not None:
            config_obj: NikGappsConfig
            if config_obj.config_package_list.__len__() > 0:
                app_set_list = config_obj.config_package_list
        else:
            config_obj = NikGappsConfig(android_version=android_version, arch=arch)

        if app_set_list is not None and app_set_list.__len__() > 0:
            file_name = package_name
            config_obj.config_package_list = Build.build_from_directory(app_set_list, android_version, arch)
            print("Exporting " + str(file_name))
            z = Export(file_name)
            result = z.zip(config_obj=config_obj, sign_zip=sign_zip, send_zip_device=send_zip_device,
                           fresh_build=fresh_build, telegram=telegram, compression_mode=Modes.DEFAULT)
            if result[1] and Config.UPLOAD_FILES:
                print("Uploading " + str(result[0]))
                execution_status, download_link, file_size_mb = upload.upload(result[0], telegram=telegram)
                print("Done")
                return execution_status
        else:
            print("Package List Empty!")
            return False

    @staticmethod
    def package(fetch_package, android_version):
        cmd = Cmd()
        if fetch_package.lower() == "all":
            fetch_package = "full"
        if Config.ADB_ROOT_ENABLED:
            if cmd.established_device_connection_as_root():
                Config.ADB_ROOT_ENABLED = True
            else:
                print("Device not found! or failed to acquire Root permissions")
                return []
        return Release.fetch_packages(fetch_package, android_version)

    @staticmethod
    def fetch_packages(fetch_package, android_version):
        # Get the list of packages that we want to pull from connected device
        app_set_list = NikGappsPackages.get_packages(fetch_package, android_version)
        # Fetch all the packages from the device
        # We will check for errors here (need to make sure we pulled all the files we were looking for
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        if app_set_list is None or app_set_list[0] is None:
            return []
        updated_pkg_list = []
        failure_summary = ""
        for app_set in app_set_list:
            app_set: AppSet
            message = "--> Working on " + app_set.title
            print(message)
            for pkg in app_set.package_list:
                pkg: Package
                pkg.validate()
                failure_summary += pkg.failure_logs
                message = pkg.package_title + " Ready to be fetched"
                print(message)
                if pkg.primary_app_location is not None or pkg.package_name is None \
                        or pkg.predefined_file_list.__len__() > 0:
                    pkg.pull_package_files(android_version=android_version, app_set=app_set.title)
                    failure_summary += pkg.failure_logs
                    message = pkg.package_title + " Successfully Fetched!"
                    print(message)
                updated_pkg_list.append(pkg)
        if not str(failure_summary).__eq__(""):
            print("")
            print("Failure Summary:")
            print(failure_summary)
        return updated_pkg_list
