import os

import pexpect

from NikGapps.helper.Statics import Statics
from NikGapps.helper.T import T


class CmdUpload:

    def __init__(self, android_version, release_type, upload_files):
        self.android_version_code = Statics.get_android_code(android_version)
        self.upload_files = upload_files
        self.host = "frs.sourceforge.net"
        self.username = "nikhilmenghani"
        self.password = os.environ.get('SF_PWD')
        self.release_dir = Statics.get_sourceforge_release_directory(release_type)
        self.release_date = T.get_london_date_time("%d-%b-%Y")
        self.child = None
        self.successful_connection = False
        if self.password is None or self.password.__eq__(""):
            self.password = ""
            self.sftp = None
            return
        self.connect_using_pexpect()

    def expect_password(self):
        self.child.expect("Password")
        self.child.sendline(str(self.password))
        print("Expecting Connected to frs.sourceforge.net or sftp> or Password")
        return self.check_successful_connection()

    def check_successful_connection(self):
        status = self.child.expect(["Connected to frs.sourceforge.net", "sftp> ", "Password"])
        if status == 0 or status == 1:
            print("Connection was successful")
            return True
        return False

    def connect_using_pexpect(self):
        self.child = pexpect.spawn('sftp nikhilmenghani@frs.sourceforge.net')
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
                self.successful_connection = self.expect_password()
            elif i == 2 or i == 3:  # TIMEOUT or EOF
                print("Timeout has occurred, let's try one more time")
                self.child.sendcontrol('c')
            else:  # other cases
                print("Connection failed")
                self.child.sendline("bye")
                try:
                    self.child.interact()
                except BaseException as e:
                    print("Exception while interacting: " + str(e))
            if self.successful_connection or i not in [0, 1, 2, 3]:
                break

