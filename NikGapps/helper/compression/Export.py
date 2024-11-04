import concurrent.futures
import concurrent.futures
import os
import threading
from multiprocessing import cpu_count
from threading import Lock

from .CompOps import CompOps
from niklibrary.compression.Modes import Modes
from niklibrary.compression.Zip import Zip
from .. import Config
from ..Assets import Assets
from niklibrary.helper.Cmd import Cmd
from niklibrary.helper.F import F
from niklibrary.helper.P import P
from niklibrary.helper.Statics import Statics
from niklibrary.helper.T import T
from niklibrary.web.TelegramApi import TelegramApi
from ...config.NikGappsConfig import NikGappsConfig


class Export:
    def __init__(self, file_name, sign=False):
        self.file_name = file_name[:-4] + "-signed.zip" if sign else file_name[:-4] + "-unofficial.zip"
        self.z = Zip(self.file_name, sign=sign, private_key_path=Assets.private_key_pem)

    def zip(self, config_obj: NikGappsConfig, telegram: TelegramApi = TelegramApi(None, None),
            compression_mode=Modes.DEFAULT, send_zip_device=Config.SEND_ZIP_DEVICE):

        build_zip = T()
        app_set_list = config_obj.config_package_list
        max_workers = cpu_count()
        lock = Lock()
        total_packages = sum(len(app_set.package_list) for app_set in app_set_list)
        completed_packages = 0
        file_sizes = ""
        zip_execution_status = False
        telegram.message(f"- Gapps is building {0:.2f}% ({completed_packages}/{total_packages})")

        def compress_and_add_file(appset, pakg, compressionmode):
            nonlocal completed_packages
            nonlocal file_sizes
            thread_id = threading.get_ident()

            pkg_zip_path = (
                    Statics.get_temp_packages_directory(config_obj.android_version, arch=config_obj.arch)
                    + Statics.dir_sep + "Packages" + Statics.dir_sep + str(pakg.package_title) + compressionmode
            )
            pkg_txt_path = pkg_zip_path.replace(compression_mode, "") + "_" + compression_mode[1:] + ".txt"

            if Config.USE_CACHED_APKS:
                print(f"Using cached package: {os.path.basename(pkg_zip_path)}")
                cached_pkg_zip_path = os.path.join(Config.CACHED_SOURCE, appset.title,
                                                   f"{pakg.package_title}{compression_mode}")
                if F.file_exists(cached_pkg_zip_path):
                    pkg_zip_path = cached_pkg_zip_path
                    pkg_txt_path = pkg_zip_path.replace(compression_mode, "") + "_" + compression_mode[
                                                                                      1:] + ".txt"
                else:
                    print(cached_pkg_zip_path + " doesn't exist!")
            else:
                CompOps.compress_package(pkg_zip_path, pakg, compression_mode)

            for size_on_file in F.read_string_file(pkg_txt_path):
                pkg_size = size_on_file
                pakg.pkg_size = pkg_size

            with lock:
                self.z.add_file(pkg_zip_path, f"AppSet/{appset.title}/{pakg.package_title}{compressionmode}")
                file_sizes = file_sizes + str(pakg.package_title) + "=" + str(pakg.pkg_size) + "\n"
                completed_packages += 1
                progress = (completed_packages / total_packages) * 100
                telegram.message(f"- Gapps is building {progress:.2f}% ({completed_packages}/{total_packages})",
                                 replace_last_message=True)
                P.blue(f"- Gapps is building {progress:.2f}% ({completed_packages}/{total_packages}): "
                       f"{appset.title}/{pakg.package_title} (Thread {thread_id})")

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for app_set in app_set_list:
                for pkg in app_set.package_list:
                    futures.append(executor.submit(compress_and_add_file, app_set, pkg, compression_mode))

        self.z.add_string(self.get_installer_script(total_packages, app_set_list, compression_mode),
                          "common/install.sh")
        self.z.add_string("#MAGISK", Statics.meta_inf_dir + "updater-script")
        self.z.add_file(Assets.magisk_update_binary, Statics.meta_inf_dir + "update-binary")
        self.z.add_string(config_obj.get_nikgapps_config(), "afzc/nikgapps.config")
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
        self.z.close()
        zip_execution_status = True
        P.green('The zip ' + self.file_name + ' is created successfully!')
        time_taken = build_zip.taken("Total time taken to build the zip")
        telegram.message("- Completed in: " + T.format_time(round(time_taken)))
        if send_zip_device:
            send_zip_device_time = T()
            cmd = Cmd()
            device_path = f"{Config.SEND_ZIP_LOCATION}/Afzc-" + str(
                config_obj.android_version) + "/" + T.get_current_time() + "/" + os.path.basename(self.file_name)
            message = f"Sending {os.path.basename(self.file_name)} to device at: " + device_path
            print(message)
            cmd.push_package(self.file_name, device_path)
            send_zip_device_time.taken("Total time taken to send the zip to device")
        return self.file_name, zip_execution_status

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
