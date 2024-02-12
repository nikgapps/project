from pathlib import Path
from subprocess import call

from ..T import T


class Zsh:

    def __init__(self, folder_to_compress, file_name):
        self.folder = folder_to_compress
        self.tarfile = str(file_name) + ".tar.xz"

    def compress(self):
        time_obj = T()
        call(["tar", "cJfP", self.tarfile, self.folder])
        print(f"zsh tar filesize: {round(Path(self.tarfile).stat().st_size / (1024 * 1024), 2)} MB")
        time_obj.taken("zsh tar filesize")
