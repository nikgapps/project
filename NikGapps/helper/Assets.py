from pathlib import Path
from importlib import resources
from NikGapps.helper.Statics import Statics
from .FileOp import FileOp
import os.path
import platform

from .Json import Json


class Assets:
    with resources.files('NikGapps.helper').joinpath('assets') as asset_path:
        assets_folder = str(asset_path)
    if not FileOp.dir_exists(assets_folder):
        assets_folder = os.path.join(os.getcwd(), 'assets')
    if not FileOp.dir_exists(assets_folder):
        pwd = Path(os.getcwd()).parent
        for folders in pwd.iterdir():
            if folders.is_dir():
                if folders.name == "assets":
                    assets_folder = str(folders)
                    break
    cwd = assets_folder + os.path.sep
    system_name = platform.system()
    apksigner_path = cwd + "apksigner.jar"
    apktool_path = cwd + "apktool_2.9.3.jar"
    key_path = cwd + "cert.pk8"
    cert_path = cwd + "cert.x509.pem"
    private_key_pem = cwd + "private_key.pem"
    if system_name == "Windows":
        aapt_path = os.path.join(assets_folder, 'bin', system_name, 'aapt2.exe')
        adb_path = os.path.join(assets_folder, 'bin', system_name, 'adb.exe')
    elif system_name == "Linux":
        aapt_path = os.path.join(assets_folder, 'bin', system_name, 'aapt2')
        adb_path = "adb"
    elif system_name == "Darwin":
        aapt_path = os.path.join(assets_folder, 'bin', system_name, 'aapt2')
        if not FileOp.file_exists(aapt_path):
            aapt_path = Statics.find_latest_aapt()
        adb_path = "adb"
    else:
        aapt_path = "adb"
        adb_path = "aapt2"
    addon_path = cwd + "addon.sh"
    header_path = cwd + "header.sh"
    functions_path = cwd + "functions.sh"
    gofile_path = cwd + "gofile.sh"
    busybox = cwd + "busybox"
    file_sizes_path = cwd + "file_size.txt"
    mount_path = cwd + "mount.sh"
    mtg_mount_path = cwd + "mtg_mount.sh"
    unmount_path = cwd + "unmount.sh"
    nikgapps_functions = cwd + "nikgapps_functions.sh"
    update_script_path = cwd + "updater-script"
    nikgapps_config = cwd + "nikgapps.config"
    debloater_config = cwd + "debloater.config"
    installer_path = cwd + "installer.sh"
    uninstaller_path = cwd + "uninstaller.sh"
    changelog = cwd + "changelogs.yaml"
    sign_jar = os.path.join(assets_folder, "NikGappsZipSigner.jar")
    customize_path = cwd + "customize.sh"
    module_path = cwd + "module.prop"
    magisk_update_binary = cwd + "magisk-update-binary.sh"
    config_versions = Json.read_dict_from_file(cwd + "config_versions.json")
    package_details = Json.read_dict_from_file(cwd + "packages.json")
    appsets_details = Json.read_dict_from_file(cwd + "appsets.json")

    @staticmethod
    def get_string_resource(file_path):
        return FileOp.read_string_file(file_path)

    @staticmethod
    def get_binary_resource(file_path):
        return FileOp.read_binary_file(file_path)
