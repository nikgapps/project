import platform

from NikGapps.helper.Assets import Assets
from NikGapps.helper.Cmd import Cmd
from NikGapps.helper.FileOp import FileOp
from NikGapps.helper.P import P
from NikGapps.helper.T import T
from NikGapps.helper.web.TelegramApi import TelegramApi


class GoFileUpload:

    @staticmethod
    def upload_file(file):
        cmd = Cmd()
        command = [f"{Assets.gofile_path}"] + [file]
        output = cmd.execute_cmd(command)
        print("Upload Log: " + str(output))
        for line in output:
            if line.startswith("https://gofile.io/"):
                return line
        return None

    @staticmethod
    def upload(file_name, telegram: TelegramApi = None):
        system_name = platform.system()
        execution_status = False
        download_link = None
        file_size_mb = None
        if telegram is not None:
            telegram.message("- The zip is uploading...")
        if system_name != "Windows":
            t = T()
            download_link = GoFileUpload.upload_file(file_name)
            P.magenta("Download Link: " + download_link)
            if download_link is None:
                P.red("Upload failed!")
                telegram.message("- Upload failed!")
                return execution_status
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
        return execution_status, download_link, file_size_mb
