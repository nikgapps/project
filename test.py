import os

from NikGapps.helper.Cmd import Cmd
from NikGapps.helper.upload.CmdUpload import CmdUpload

# upload = CmdUpload('13', 'stable', True)
# print(upload.successful_connection)
# upload.create_directory_structure("A/B/C")

import pexpect
import socket

hostname = socket.gethostname()
ip_address = socket.gethostbyname(hostname)
print(f"Hostname: {hostname}")
print(f"IP Address: {ip_address}")


password = os.environ.get('SF_PWD')
child = pexpect.spawn('sftp nikhilmenghani@frs.sourceforge.net')  # replace with your user and host
i = child.expect(["Password", "yes/no", pexpect.TIMEOUT, pexpect.EOF], timeout=120)
print(i)
print(child.before)
print(child)
child.sendline(str(password))
print(child.before)
print(child)
