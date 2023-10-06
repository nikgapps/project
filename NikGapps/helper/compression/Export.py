from .. import Config
from ..NikGappsConfig import NikGappsConfig
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


class Export:
    def __init__(self, file_name):
        self.file_name = file_name
        self.z = Zip(file_name)

    def zip(self, config_obj: NikGappsConfig, sign_zip, send_zip_device, fresh_build, telegram: TelegramApi,
            compression_mode=Modes.DEFAULT):
        app_set_list = config_obj.config_package_list
        config_string = config_obj.get_nikgapps_config(config_dict=config_obj.config_dict)
        android_version = config_obj.android_version
        total_packages = 0
        print_progress = ""
        build_zip = T()
        file_sizes = ""
        zip_execution_status = False
        try:
            app_set_count = len(app_set_list)
            app_set_index = 1
            telegram.message("- Gapps is building...")
            for app_set in app_set_list:
                app_set: AppSet
                app_set_progress = round(float(100 * app_set_index / app_set_count))
                telegram.message(
                    f"- Gapps is building... {str(app_set_progress)}% done {Statics.display_progress(int(app_set_progress))}",
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
                    pkg_txt_path = pkg_zip_path.replace(compression_mode, ".txt")
                    print_value = "AppSet (" + str(
                        app_set_progress) + "%): " + app_set.title + " Zipping (" + str(
                        package_progress) + "%): " + pkg.package_title
                    print(print_value)
                    print_progress = print_progress + "\n" + print_value
                    file_exists = FileOp.file_exists(pkg_zip_path)
                    txt_file_exists = FileOp.file_exists(pkg_txt_path)
                    old_file = True if (
                            file_exists and T.get_mtime(pkg_zip_path) < T.get_local_date_time()) else False
                    if (fresh_build and old_file) or (not file_exists) or (not txt_file_exists):
                        cpkg = CompOps.get_compression_obj(pkg_zip_path, compression_mode)
                        file_index = 1
                        for x in pkg.file_dict:
                            file_index = file_index + 1
                            pkg_size = pkg_size + Statics.get_file_bytes(x)
                            cpkg.add_file(x, str(x)[str(x).find("___"):].replace("\\", "/"))
                        if pkg.clean_flash_only:
                            cpkg.add_string("", "___etc___permissions/" + pkg.package_title + ".prop")
                        pkg.pkg_size = pkg_size
                        cpkg.add_string(pkg.get_installer_script(str(pkg_size)), "installer.sh")
                        cpkg.add_string(pkg.get_uninstaller_script(), "uninstaller.sh")
                        cpkg.close()
                        FileOp.write_string_file(str(pkg_size), pkg_txt_path)
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
            self.z.add_file(Assets.addon_path, "common/addon")
            self.z.add_file(Assets.header_path, "common/header")
            self.z.add_file(Assets.functions_path, "common/functions")
            self.z.add_string(file_sizes, "common/file_size")
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
            telegram.message("- Completed in: " + str(round(time_taken)) + " seconds")
            file_name = self.file_name
            if sign_zip:
                sign_zip_time = T()
                print('Signing The Zip')
                telegram.message("- The zip is Signing...")
                # the issue (cannot access class sun.security.pkcs.SignerInfo) is pending with Java 17
                # https://intellij-support.jetbrains.com/hc/en-us/community/posts/5153987456018-Java-17-cannot-access-class-sun-security-pkcs-PKCS7
                zip_execution_status = False
                cmd = Cmd()
                output_list = cmd.sign_zip_file(file_name)
                for output in output_list:
                    if output.__eq__("Success!"):
                        file_name = file_name[:-4] + "-signed.zip"
                        print("The zip signed successfully: " + file_name)
                        zip_execution_status = True
                    elif output.startswith("Exception occurred while executing"):
                        print("The zip could not be signed: " + output)
                        telegram.message("- The zip could not be signed: " + output)
                time_taken = sign_zip_time.taken("Total time taken to sign the zip")
                if zip_execution_status:
                    telegram.message("- The zip signed in: " + str(round(time_taken)) + " seconds",
                                     replace_last_message=True)
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
                                       key=lambda app__set: sum(pakg.pkg_size for pakg in app__set.package_list),
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
