import os
import platform
from pathlib import Path
import pysftp
from NikGapps.helper.FileOp import FileOp
from NikGapps.helper.P import P
from NikGapps.helper.Statics import Statics
from NikGapps.helper.T import T
from NikGapps.helper.web.TelegramApi import TelegramApi


class Upload:
    def __init__(self, android_version, release_type, upload_files, password=None):
        self.android_version_code = Statics.get_android_code(android_version)
        self.upload_files = upload_files
        self.host = "frs.sourceforge.net"
        self.username = "nikhilmenghani"
        self.password = os.environ.get('SF_PWD') if password is None else password
        self.release_dir = Statics.get_sourceforge_release_directory(release_type)
        self.release_date = T.get_london_date_time("%d-%b-%Y")
        self.cmd_method = False  # can be removed later
        self.upload_obj = None  # can be removed later
        if self.password is None or self.password.__eq__(""):
            self.password = ""
            self.sftp = None
            return
        try:
            self.sftp = pysftp.Connection(host=self.host, username=self.username, password=self.password)
        except Exception as e:
            P.red("Exception while connecting to SFTP: " + str(e))
            self.sftp = None

    def set_release_dir(self, release_dir):
        self.release_dir = release_dir

    def get_cd(self, file_type):
        folder_name = "Test"
        match file_type:
            case "gapps":
                folder_name = "NikGapps-" + self.android_version_code
            case "config":
                folder_name = "NikGapps-" + self.android_version_code
                return self.release_dir + "/" + folder_name
            case "addons":
                folder_name = "Addons-" + self.android_version_code
            case "debloater":
                folder_name = "Debloater"
            case _:
                print(file_type)
        print("Upload Dir: " + self.release_dir + "/" + folder_name)
        return self.release_dir + "/" + folder_name + "/" + self.release_date

    def upload(self, file_name, telegram: TelegramApi = None, remote_directory=None):
        if self.sftp is not None:
            system_name = platform.system()
            execution_status = False
            download_link = None
            file_size_kb = round(FileOp.get_file_size(file_name, "KB"), 2)
            file_size_mb = round(FileOp.get_file_size(file_name), 2)
            if telegram is not None:
                telegram.message(f"- The zip {file_size_mb} MB is uploading...")
            if self.sftp is not None and system_name != "Windows" and self.upload_files:
                t = T()
                file_type = "gapps"
                if os.path.basename(file_name).__contains__("-Addon-"):
                    file_type = "addons"
                elif os.path.basename(file_name).__contains__("Debloater"):
                    file_type = "debloater"

                if remote_directory is None:
                    remote_directory = self.get_cd(file_type)

                remote_filename = Path(file_name).name
                try:
                    self.sftp.chdir(remote_directory)
                except IOError:
                    P.magenta(f"The remote directory: {remote_directory} doesn't exist, creating..")
                    try:
                        self.sftp.makedirs(remote_directory)
                        self.sftp.chdir(remote_directory)
                    except Exception as e:
                        P.red("Exception while creating directory: " + str(e))
                        self.close_connection()
                        self.sftp = pysftp.Connection(host=self.host, username=self.username, password=self.password)
                        return execution_status
                putinfo = self.sftp.put(file_name, remote_filename)
                print(putinfo)
                P.green(f'File uploaded successfully to {remote_directory}/{remote_filename}')
                download_link = Statics.get_download_link(file_name, remote_directory)
                P.magenta("Download Link: " + download_link)
                print("uploading file finished...")
                execution_status = True
                time_taken = t.taken(f"Total time taken to upload file with size {file_size_mb} MB ("
                                     f"{file_size_kb} Kb)")
                if execution_status:
                    if telegram is not None:
                        telegram.message(
                            f"- The zip {file_size_mb} MB uploaded in {T.format_time(round(time_taken))}\n",
                            replace_last_message=True)
                        if download_link is not None:
                            telegram.message(f"*Note:* Download link should start working in 10 minutes",
                                             escape_text=False,
                                             ur_link={f"Download": f"{download_link}"})
            else:
                P.red("System incompatible or upload disabled or connection failed!")
                P.red("system_name: " + system_name)
                P.red("self.sftp: " + str(self.sftp))
                P.red("self.upload_files: " + str(self.upload_files))
            return execution_status, download_link, file_size_mb
        else:
            P.red("Connection failed!")
            return False, None, None

    def close_connection(self):
        if self.cmd_method:
            self.upload_obj.close_connection()
        elif self.sftp is not None:
            self.sftp.close()
            print("Connection closed")
