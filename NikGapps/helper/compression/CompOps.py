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
