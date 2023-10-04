import os
import platform
import time
from pathlib import Path
import pexpect
from NikGapps.helper.FileOp import FileOp
from NikGapps.helper.P import P
from NikGapps.helper.Statics import Statics
from NikGapps.helper.T import T
from NikGapps.helper.web.TelegramApi import TelegramApi


class CmdUpload:

    def __init__(self, android_version, release_type, upload_files, password=None):
        self.android_version_code = Statics.get_android_code(android_version)
        self.upload_files = upload_files
        self.host = "frs.sourceforge.net"
        self.username = "nikhilmenghani"
        self.password = os.environ.get('SF_PWD') if password is None else password
        self.release_dir = Statics.get_sourceforge_release_directory(release_type)
        self.release_date = T.get_london_date_time("%d-%b-%Y")
        self.child = None
        self.successful_connection = False
        if self.password is None or self.password.__eq__(""):
            self.password = ""
            self.sftp = None
            P.red("Password is not set, please set the password in environment variable SF_PWD")
            return
        self.connect_using_pexpect()

    def expect_password(self):
        self.child.sendline(str(self.password))
        print(f"Expecting Connected to {self.host} or sftp> or Password")
        return self.check_successful_connection()

    def check_successful_connection(self):
        status = self.child.expect([f"Connected to {self.host}", "sftp> ", "Password"])
        if status == 0 or status == 1:
            print("Connection was successful")
            return True
        return False

    def connect_using_pexpect(self):
        self.child = pexpect.spawn(f'sftp {self.username}@{self.host}')
        tried_twice = False
        print("Expecting Password")
        while True:
            i = self.child.expect(["Password", "yes/no", pexpect.TIMEOUT, pexpect.EOF], timeout=120)
            if i == 0:  # Password
                print("Sending Password")
                self.successful_connection = self.expect_password()
            elif i == 1:  # yes/no
                print("sending yes")
                self.child.sendline("yes")
                print("Expecting Password")
                self.child.expect("Password")
                self.successful_connection = self.expect_password()
            elif i == 2 or i == 3:  # TIMEOUT or EOF
                if not tried_twice:
                    print("Timeout has occurred, let's try one more time")
                    # self.child.sendcontrol('c')
                    self.close_connection()
                    self.child = pexpect.spawn('sftp nikhilmenghani@frs.sourceforge.net')
                    tried_twice = True
                else:
                    print("Connection failed")
                    break
            else:  # other cases
                print("Connection failed")
                self.close_connection()
                try:
                    self.child.interact()
                except BaseException as e:
                    print("Exception while interacting: " + str(e))
            if self.successful_connection or i not in [0, 1, 2, 3]:
                break

    def navigate_to_directory(self, directory):
        self.child.expect('sftp>')
        self.child.sendline(f'cd {directory}')

    def create_directory_structure(self, remote_directory):
        # Split the directory path into components
        remote_directory = remote_directory.replace(f"{self.release_dir}/", '')
        directories = remote_directory.split('/')
        # cd to the root directory
        self.navigate_to_directory(self.release_dir)
        # Create each directory in the path separately
        for i in range(len(directories)):
            path = '/'.join(directories[:i + 1])
            print(f"Creating directory {self.release_dir}/{path}")
            self.child.expect('sftp>')
            self.child.sendline(f'mkdir {path}')

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

    def upload_file(self, file_path, remote_path):
        self.child.sendline("put " + file_path + " " + remote_path)
        self.child.expect("Uploading")
        self.child.expect("100%", timeout=3600)
        self.child.expect("sftp>")
        time.sleep(1)

    def upload(self, file_name, telegram: TelegramApi = None, remote_directory=None):
        execution_status = False
        download_link = None
        file_size_mb = None
        if self.successful_connection:
            system_name = platform.system()
            if telegram is not None:
                telegram.message("- The zip is uploading...")
            if system_name != "Windows" and self.upload_files:
                t = T()
                file_type = "gapps"
                if os.path.basename(file_name).__contains__("-Addon-"):
                    file_type = "addons"
                elif os.path.basename(file_name).__contains__("Debloater"):
                    file_type = "debloater"

                if remote_directory is None:
                    remote_directory = self.get_cd(file_type)

                remote_filename = Path(file_name).name
                self.create_directory_structure(remote_directory)
                self.navigate_to_directory(remote_directory)
                self.upload_file(file_name, remote_filename)
                P.green(f'File uploaded successfully to {remote_directory}/{remote_filename}')
                download_link = Statics.get_download_link(file_name, remote_directory)
                P.magenta("Download Link: " + download_link)
                print("uploading file finished...")
                execution_status = True
                file_size_kb = round(FileOp.get_file_size(file_name, "KB"), 2)
                file_size_mb = round(FileOp.get_file_size(file_name), 2)
                time_taken = t.taken(f"Total time taken to upload file with size {file_size_mb} MB ("
                                     f"{file_size_kb} Kb)")
                if execution_status:
                    if telegram is not None:
                        telegram.message(
                            f"- The zip {file_size_mb} MB uploaded in {str(round(time_taken))} seconds\n",
                            replace_last_message=True)
                        if download_link is not None:
                            telegram.message(f"*Note:* Download link should start working in 10 minutes", escape_text=False,
                                             ur_link={f"Download": f"{download_link}"})
            else:
                P.red("System incompatible or upload disabled or connection failed!")
        else:
            P.red("Connection failed!")
        return execution_status, download_link, file_size_mb

    def close_connection(self):
        if not str(self.password).__eq__(""):
            self.child.sendline("bye")
            self.child.close()
