import os.path
from pathlib import Path
from .Assets import Assets
from .Statics import Statics
from .XmlOp import XmlOp
from .Cmd import Cmd
from .FileOp import FileOp
from .overlay.Overlay import Overlay


class Package:
    def __init__(self, title, package_name, app_type = None, package_title=None, partition=None):
        self.package_name = package_name
        self.title = title
        self.package_title = package_title
        if package_title is None:
            self.package_title = title
        self.partition = partition
        if partition is None:
            self.partition = "product"
        self.app_type = app_type  # Whether the Package is system app or private app
        # target_folder is the folder where the package will be installed
        if app_type == Statics.is_priv_app:
            self.target_folder = str(Statics.system_root_dir + "/" + "priv-app" + "/" + title).replace("\\\\", "/")
        elif app_type == Statics.is_system_app:
            self.target_folder = str(Statics.system_root_dir + "/" + "app" + "/" + title).replace("\\\\", "/")
        self.install_list = []  # Stores list of files installed to the package directory
        self.predefined_file_list = []  # Stores list of predefined file list
        self.overlay_list = []  # Stores list of overlay apks
        self.framework_list = []  # Stores list of Framework files
        self.primary_app_location = None  # This will help generate priv-app whitelist permissions
        self.folder_dict = dict()  # Stores list of folders that needs 755 permissions
        self.file_dict = dict()  # Stores the file location on server as key and on device as value
        self.delete_files_list = []  # Stores the path of file to delete. Helpful for removing AOSP counterpart
        self.priv_app_permissions = []  # Stores the priv-app whitelist permissions for the package
        self.delete_overlay_list = []  # Stores the list of overlays to delete
        self.enabled = 1
        self.validated = True
        self.clean_flash_only = False
        self.additional_installer_script = ""
        self.failure_logs = ""
        self.pkg_size = 0
        self.validation_script = None
        self.addon_index = "09"

    def add_overlay(self, overlay: Overlay):
        for overlay_item in self.overlay_list:
            if overlay_item.apk_name == overlay.apk_name:
                return
        self.overlay_list.append(overlay)

    def delete_overlay(self, overlay):
        if overlay not in self.delete_overlay_list:
            self.delete_overlay_list.append(overlay)

    def delete(self, data):
        if not str(data).startswith("/"):
            if data not in self.delete_files_list:
                self.delete_files_list.append(data)
        else:
            if data not in self.delete_files_list:
                self.delete_files_list.append(data)

    # this will generate the xml providing white-list permissions to the package
    def generate_priv_app_whitelist(self, app_set, permissions_list, android_version, pkg_path=None):
        for perm in self.priv_app_permissions:
            if perm not in permissions_list:
                permissions_list.append(perm)
        permissions_path = "/etc/permissions/" + str(self.package_name) + ".xml"
        import_path = Statics.get_import_path(app_set, self.package_title, permissions_path, android_version,
                                              pkg_path)
        self.file_dict[import_path] = "etc/permissions/" + str(self.package_name) + ".xml"
        XmlOp(self.package_name, permissions_list, import_path)

    def get_installer_script(self, pkg_size):
        lines = Assets.get_string_resource(Assets.installer_path)
        str_data = ""
        for line in lines:
            str_data += line

        str_data += "# Initialize the variables\n"
        str_data += "default_partition=\"" + self.partition + "\"\n"
        str_data += "clean_flash_only=\"" + str(self.clean_flash_only).lower() + "\"\n"
        str_data += "product_prefix=$(find_product_prefix \"$install_partition\")\n"
        str_data += "title=\"" + self.title + "\"\n"
        str_data += "package_title=\"" + self.package_title + "\"\n"
        str_data += "pkg_size=\"" + pkg_size + "\"\n"
        if self.package_name is not None:
            str_data += "package_name=\"" + self.package_name + "\"\n"
        else:
            str_data += "package_name=\"\"" + "\n"
        str_data += "packagePath=install" + self.package_title + "Files\n"
        str_data += "deleteFilesPath=delete" + self.package_title + "Files\n"
        str_data += "propFilePath=$(get_prop_file_path $package_title)\n"
        str_data += "\n"
        str_data += f"remove_aosp_apps_from_rom=\"\n"
        for delete_folder in self.delete_files_list:
            str_data += f"{delete_folder}\n"
        str_data += "\"\n"
        str_data += "\n"
        str_data += f"delete_overlays=\"\n"
        for delete_overlay in self.delete_overlay_list:
            str_data += f"{delete_overlay}\n"
        str_data += "\"\n"
        str_data += "\n"
        str_data += f"file_list=\"\n"
        for file in self.file_dict:
            str_data += str(file)[str(file).find("___"):].replace("\\", "/") + "\n"
        str_data += "\"\n"
        str_data += "\n"
        str_data += "remove_overlays() {\n"
        str_data += "   for i in $delete_overlays; do\n"
        str_data += "       delete_overlays \"$i\" \"$propFilePath\" \"$package_title\" \n"
        str_data += "   done\n"
        str_data += "}\n"
        str_data += "\n"
        str_data += "remove_existing_package() {\n"
        str_data += "   # remove the existing folder for clean install of " + self.package_title + "\n"
        str_data += "   delete_package \"" + self.title + "\" \"$package_title\" \n"
        # str_data += " # remove the data of package"
        # str_data += " delete_package_data \"" + self.package_name + "\"\n"
        str_data += "}\n"
        str_data += "\n"
        str_data += "remove_aosp_apps() {\n"
        str_data += "   # Delete the folders that we want to remove with installing " + self.package_title + "\n"
        str_data += "   for i in $remove_aosp_apps_from_rom; do\n"
        str_data += "       RemoveAospAppsFromRom \"$i\" \"$propFilePath\" \"$package_title\" \n"
        str_data += "   done\n"
        str_data += "}\n"
        str_data += "\n"
        str_data += "install_package() {\n"
        str_data += "   remove_existing_package\n"
        str_data += "   remove_aosp_apps\n"
        str_data += "   remove_overlays\n"
        str_data += "   # Create folders and set the permissions\n"
        for folder in self.folder_dict:
            str_data += "   make_dir \"" + folder + "\"\n"
        str_data += "\n"
        str_data += "   delete_prop_lines \"$propFilePath\"\n"
        str_data += "\n"
        str_data += "   # Copy the files and set the permissions\n"
        str_data += "   for i in $file_list; do\n"
        str_data += "       install_file \"$i\"\n"
        str_data += "   done\n"
        str_data += "\n"
        if not str(self.additional_installer_script).__eq__(""):
            str_data += self.additional_installer_script
            str_data += "\n"
        str_data += "   chmod 755 \"$COMMONDIR/addon.sh\";\n"
        str_data += "   update_prop \"$propFilePath\"" \
                    " \"install\"" \
                    " \"$propFilePath\" \"" + self.package_title + "\" \n"
        str_data += "   . $COMMONDIR/addon.sh \"" + self.package_title + "\" \"$propFilePath\" " + f"\"{self.addon_index}\"\n"
        str_data += "   copy_file \"$propFilePath\" \"$logDir/addonfiles/" + "$package_title.prop" + "\"\n"
        str_data += "}\n"
        str_data += "\n"
        str_data += self.validation_script + "\n" if self.validation_script is not None else "find_install_mode\n"
        str_data += "\n"
        return str_data

    def get_uninstaller_script(self):
        lines = Assets.get_string_resource(Assets.uninstaller_path)
        str_data = ""
        for line in lines:
            str_data += line
        str_data += "\n\n"
        str_data += "# Initialize the variables\n"
        str_data += "uninstall_addon=$1\n"
        str_data += "clean_flash_only=\"" + str(self.clean_flash_only).lower() + "\"\n"
        str_data += "title=\"" + self.title + "\"\n"
        str_data += "package_title=\"" + self.package_title + "\"\n"
        if self.package_name is not None:
            str_data += "package_name=\"" + self.package_name + "\"\n"
        else:
            str_data += "package_name=\"\"" + "\n"
        str_data += "\n"
        str_data += f"file_list=\"\n"
        for file in self.file_dict:
            str_data += str(file)[str(file).find("___"):].replace("\\", "/") + "\n"
        str_data += "\"\n"
        str_data += "\n"
        str_data += "uninstall_package"
        str_data += "\n"
        return str_data
