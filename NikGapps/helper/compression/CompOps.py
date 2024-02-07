from NikGapps.helper.FileOp import FileOp
from NikGapps.helper.Statics import Statics
from NikGapps.helper.Package import Package
from .Modes import Modes


class CompOps:

    @staticmethod
    def get_compression_obj(file_name, compression_mode=Modes.ZIP):
        match compression_mode:
            case Modes.TAR_XZ:
                from .Tar import Tar
                return Tar(file_name)
            case _:
                from .Zip import Zip
                return Zip(file_name)

    @staticmethod
    def compress_package(pkg_zip_path, pkg: Package, compression_mode=Modes.DEFAULT):
        try:
            pkg_size = 0
            pkg_txt_path = pkg_zip_path.replace(compression_mode, "") + "_" + compression_mode[1:] + ".txt"
            cpkg = CompOps.get_compression_obj(pkg_zip_path, compression_mode=compression_mode)
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
        except Exception as e:
            print(e)
            return False
        return True
