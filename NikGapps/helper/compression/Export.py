from .. import Config
from ..P import P
from ..FileOp import FileOp
from ..Assets import Assets
from ..Package import Package
from ..AppSet import AppSet
from ..Cmd import Cmd
import os
from .Zip import Zip
from .CompOps import CompOps
from .Modes import Modes
from ..Statics import Statics
from ..T import T
from ..web.TelegramApi import TelegramApi
from ...config.NikGappsConfig import NikGappsConfig


class Export:
    def __init__(self, file_name, sign=False):
        self.file_name = file_name[:-4] + "-signed.zip" if sign else file_name[:-4] + "-unofficial.zip"
        self.z = Zip(self.file_name, sign=sign, private_key_path=Assets.private_key_pem)

    def zip(self, config_obj: NikGappsConfig, telegram: TelegramApi,
            compression_mode=Modes.DEFAULT, send_zip_device=Config.SEND_ZIP_DEVICE, fresh_build=Config.FRESH_BUILD):
        app_set_list = config_obj.config_package_list
        config_string = config_obj.get_nikgapps_config()
        android_version = config_obj.android_version
        total_packages = 0
        print_progress = ""
        build_zip = T()
        file_sizes = ""
        zip_execution_status = False
        arch = "" if config_obj.arch == "arm64" else "_" + config_obj.arch
        cache_source_dir = Statics.pwd + Statics.dir_sep + str(
            android_version) + arch + "_cached" if Config.USE_CACHED_APKS else ""
        try:
            app_set_count = len(app_set_list)
            app_set_index = 1
            telegram.message("- Gapps is building...")
            for app_set in app_set_list:
                app_set: AppSet
                app_set_progress = round(float(100 * app_set_index / app_set_count))
                telegram.message(
                    f"- Gapps is building... {str(app_set_progress)}% done",
                    replace_last_message=True)
                package_count = len(app_set.package_list)
                package_index = 0
                for pkg in app_set.package_list:
                    pkg_size = 0
                    # Creating <Packages>.zip for all the packages
                    pkg: Package
                    package_progress = round(float(100 * package_index / package_count))
                    pkg_zip_path = Statics.get_temp_packages_directory(
                        android_version, arch=config_obj.arch) + Statics.dir_sep + "Packages" + Statics.dir_sep + str(
                        pkg.package_title) + compression_mode
                    pkg_txt_path = pkg_zip_path.replace(compression_mode, "") + "_" + compression_mode[1:] + ".txt"
                    print_value = "AppSet (" + str(
                        app_set_progress) + "%): " + app_set.title + " Zipping (" + str(
                        package_progress) + "%): " + pkg.package_title
                    print(print_value)
                    print_progress = print_progress + "\n" + print_value
                    cached_pkg_zip_path = os.path.join(cache_source_dir, app_set.title,
                                                       f"{pkg.package_title}{compression_mode}")
                    if FileOp.file_exists(cached_pkg_zip_path):
                        pkg_zip_path = cached_pkg_zip_path
                        pkg_txt_path = pkg_zip_path.replace(compression_mode, "") + "_" + compression_mode[
                                                                                          1:] + ".txt"
                    file_exists = FileOp.file_exists(pkg_zip_path)
                    txt_file_exists = FileOp.file_exists(pkg_txt_path)
                    old_file = True if (
                            file_exists and T.get_mtime(pkg_zip_path) < T.get_local_date_time()) else False
                    if cache_source_dir.__eq__("") and (
                            (fresh_build and old_file) or (not file_exists) or (not txt_file_exists)):
                        CompOps.compress_package(pkg_zip_path, pkg, compression_mode)
                    else:
                        print(f"Using cached package: {os.path.basename(pkg_zip_path)}")
                    for size_on_file in FileOp.read_string_file(pkg_txt_path):
                        pkg_size = size_on_file
                        pkg.pkg_size = pkg_size
                    self.z.add_file(pkg_zip_path,
                                    "AppSet/" + str(app_set.title) + "/" + str(pkg.package_title) + compression_mode)
                    package_index = package_index + 1
                    total_packages += 1
                    file_sizes = file_sizes + str(pkg.package_title) + "=" + str(pkg_size) + "\n"
                app_set_index = app_set_index + 1
            # Writing additional script files to the zip
            self.z.add_string(self.get_installer_script(total_packages, app_set_list, compression_mode),
                              "common/install.sh")
            self.z.add_string("#MAGISK", Statics.meta_inf_dir + "updater-script")
            self.z.add_file(Assets.magisk_update_binary, Statics.meta_inf_dir + "update-binary")
            self.z.add_string(config_string, "afzc/nikgapps.config")
            debloater_config_lines = ""
            for line in Assets.get_string_resource(Assets.debloater_config):
                debloater_config_lines += line
            for line in config_obj.debloater_list:
                debloater_config_lines += line + "\n"
            self.z.add_string(debloater_config_lines, "afzc/debloater.config")
            self.z.add_file(Assets.changelog, "changelog.yaml")
            self.z.add_file(Assets.addon_path, "common/addon.sh")
            self.z.add_file(Assets.header_path, "common/header.sh")
            self.z.add_file(Assets.functions_path, "common/functions.sh")
            self.z.add_string(file_sizes, "common/file_size.txt")
            self.z.add_file(Assets.nikgapps_functions, "common/nikgapps_functions.sh")
            self.z.add_file(Assets.mount_path, "common/mount.sh")
            self.z.add_file(Assets.mtg_mount_path, "common/mtg_mount.sh")
            self.z.add_file(Assets.unmount_path, "common/unmount.sh")
            self.z.add_string(os.path.basename(os.path.splitext(self.file_name)[0]), "zip_name.txt")
            self.z.add_string(f"Created by {config_obj.creator}".center(38, ' '), "creator.txt")
            self.z.add_string(self.get_customize_sh(self.file_name), "customize.sh")
            self.z.add_file(Assets.module_path, "module.prop")
            self.z.add_file(Assets.busybox, "busybox")
            zip_execution_status = True
            P.green('The zip ' + self.file_name + ' is created successfully!')
        except Exception as e:
            print("Exception occurred while creating the zip " + str(e))
        finally:
            self.z.close()
            time_taken = build_zip.taken("Total time taken to build the zip")
            telegram.message("- Completed in: " + T.format_time(round(time_taken)))
            file_name = self.file_name
            if send_zip_device:
                send_zip_device_time = T()
                cmd = Cmd()
                device_path = f"{Config.SEND_ZIP_LOCATION}/Afzc-" + str(
                    android_version) + "/" + T.get_current_time() + "/" + os.path.basename(
                    file_name)
                message = f"Sending {os.path.basename(file_name)} to device at: " + device_path
                print(message)

                cmd.push_package(file_name, device_path)
                send_zip_device_time.taken("Total time taken to send the zip to device")
            return file_name, zip_execution_status

    @staticmethod
    def get_installer_script(total_packages, app_set_list, compression_mode=Modes.DEFAULT):
        delem = ","
        installer_script_path_string = "#!/sbin/sh\n"
        installer_script_path_string += "# Shell Script EDIFY Replacement\n\n"
        core_app_sets = []
        other_app_sets = []
        for app_set in app_set_list:
            if app_set.title in ['Core', 'CoreGo']:
                core_app_sets.append(app_set)
            else:
                other_app_sets.append(app_set)
        sorted_other_app_sets = sorted(other_app_sets,
                                       key=lambda app__set: sum(int(pakg.pkg_size) for pakg in app__set.package_list),
                                       reverse=True)
        sorted_app_sets = core_app_sets + sorted_other_app_sets
        progress_max = 0.9
        progress_per_package = 0
        if total_packages > 0:
            progress_per_package = round(progress_max / total_packages, 2)
        install_progress = 0
        installer_script_path_string += f"ProgressBarValues=\"\n"
        for app_set in sorted_app_sets:
            sorted_packages = sorted(app_set.package_list, key=lambda pakg: pakg.pkg_size, reverse=True)
            for pkg in sorted_packages:
                install_progress += progress_per_package
                if install_progress > 1.0:
                    install_progress = 1.0
                installer_script_path_string += f"{pkg.package_title}={str(round(install_progress, 2))}\n"
        installer_script_path_string += "\"\n\n"

        for app_set in sorted_app_sets:
            sorted_packages = sorted(app_set.package_list, key=lambda pakg: pakg.pkg_size, reverse=True)
            installer_script_path_string += f"{app_set.title}=\"\n"
            for pkg in sorted_packages:
                installer_script_path_string += f"{pkg.package_title}{delem}{pkg.pkg_size}{delem}{pkg.partition}\n"
            installer_script_path_string += "\"\n\n"

        for app_set in sorted_app_sets:
            installer_script_path_string += "install_app_set \"" + \
                                            app_set.title + "\" \"$" + \
                                            app_set.title + "\" \"" + \
                                            compression_mode + "\" \n"

        installer_script_path_string += "\nset_progress 1.00" + "\n\n"
        installer_script_path_string += "exit_install" + "\n\n"
        return installer_script_path_string

    @staticmethod
    def get_customize_sh(file_name):
        customize_path_string = "actual_file_name=" + os.path.basename(os.path.splitext(file_name)[0]) + "\n"
        lines = Assets.get_string_resource(Assets.customize_path)
        for line in lines:
            customize_path_string += line
        return customize_path_string
