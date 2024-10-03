from niklibrary.helper.F import F
from niklibrary.helper.Statics import Statics
from NikGapps.helper.Package import Package
from niklibrary.compression.Modes import Modes


class CompOps:

    @staticmethod
    def get_compression_obj(file_name, compression_mode=Modes.ZIP):
        match compression_mode:
            case Modes.TAR_XZ:
                from niklibrary.compression.Tar import Tar
                return Tar(file_name)
            case _:
                from niklibrary.compression.Zip import Zip
                return Zip(file_name)

    @staticmethod
    def compress_package(pkg_zip_path, pkg: Package, compression_mode=Modes.DEFAULT):
        try:
            pkg_size = 0
            pkg_txt_path = pkg_zip_path.replace(compression_mode, "") + "_" + compression_mode[1:] + ".txt"
            cpkg = CompOps.get_compression_obj(pkg_zip_path, compression_mode=compression_mode)
            file_index = 1
            for x in pkg.file_dict:
                y = pkg.file_dict[x]
                file_index = file_index + 1
                pkg_size = pkg_size + Statics.get_file_bytes(x)
                cpkg.add_file(x, y)
            if pkg.clean_flash_only:
                cpkg.add_string("", "___etc___permissions/" + pkg.package_title + ".prop")
            pkg.pkg_size = pkg_size
            if pkg.priv_app_permissions_str is not None:
                cpkg.add_string(pkg.priv_app_permissions_str, "___etc___permissions/" + pkg.package_name + ".xml")
            cpkg.add_string(pkg.get_installer_script(str(pkg_size)), "installer.sh")
            cpkg.add_string(pkg.get_uninstaller_script(), "uninstaller.sh")
            cpkg.close()
            F.write_string_file(str(pkg_size), pkg_txt_path)
        except Exception as e:
            print(e)
            return False
        return True
