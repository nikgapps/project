import os
from pathlib import Path


class C:
    @staticmethod
    def find_cwd():
        cwd = os.getcwd()
        if "requirements.txt" in os.listdir(cwd):
            return cwd
        parent_dir = str(Path(cwd).parent)
        if "requirements.txt" in os.listdir(parent_dir):
            return parent_dir
        return cwd

    ds = os.path.sep
