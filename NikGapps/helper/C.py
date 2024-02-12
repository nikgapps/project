import os
from pathlib import Path


class C:
    @staticmethod
    def find_cwd():
        cwd = os.getcwd()
        for file in os.listdir(str(Path(cwd).parent)):
            if file.__eq__("requirements.txt"):
                return str(Path(cwd).parent)
