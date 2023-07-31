from NikGapps.helper.upload.CmdUpload import CmdUpload

upload = CmdUpload('13', 'stable', True)
print(upload.successful_connection)
upload.create_directory_structure("A/B/C")

