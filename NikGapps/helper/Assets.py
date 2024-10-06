from pathlib import Path
from importlib import resources

from niklibrary.helper.Assets import Assets as A
from niklibrary.helper.F import F
import os.path

from niklibrary.json.Json import Json


class Assets:
    with resources.files('NikGapps.helper').joinpath('assets') as asset_path:
        assets_folder = str(asset_path)
    if not F.dir_exists(assets_folder):
        assets_folder = os.path.join(os.getcwd(), 'assets')
    if not F.dir_exists(assets_folder):
        pwd = Path(os.getcwd()).parent
        for folders in pwd.iterdir():
            if folders.is_dir():
                if folders.name == "assets":
                    assets_folder = str(folders)
                    break
    cwd = assets_folder + os.path.sep
    system_name = A.system_name
    apksigner_path = A.get("apksigner.jar")
    apktool_path = A.get("apktool_2.10.0.jar")
    key_path = A.get("cert.pk8")
    cert_path = A.get("cert.x509.pem")
    private_key_pem = A.get("private_key.pem")
    aapt_path = A.aapt_path
    adb_path = A.adb_path
    addon_path = cwd + "addon.sh"
    header_path = cwd + "header.sh"
    functions_path = cwd + "functions.sh"
    busybox = A.get("busybox")
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
    sign_jar = os.path.join(A.assets_folder, "NikGappsZipSigner.jar")
    customize_path = cwd + "customize.sh"
    module_path = cwd + "module.prop"
    magisk_update_binary = cwd + "magisk-update-binary.sh"
    config_versions = Json.read_dict_from_file(cwd + "config_versions.json")
    package_details = Json.read_dict_from_file(cwd + "packages.json")
    appsets_details = Json.read_dict_from_file(cwd + "appsets.json")

    @staticmethod
    def get_string_resource(file_path):
        return F.read_string_file(file_path)

    @staticmethod
    def get_binary_resource(file_path):
        return F.read_binary_file(file_path)
