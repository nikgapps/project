import zipfile
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.backends import default_backend
import os


class ZipSigner:
    def __init__(self, private_key_path, password=None):
        self.private_key = self.load_private_key(private_key_path, password)

    def load_private_key(self, file_path, password):
        with open(file_path, 'rb') as key_file:
            private_key = load_pem_private_key(
                key_file.read(),
                password=password,
                backend=default_backend()
            )
        return private_key

    def create_signed_zip(self, input_files, output_zip, comment=b''):
        with zipfile.ZipFile(output_zip, 'w') as myzip:
            for file_path in input_files:
                self.add_and_sign_file(myzip, file_path)
            myzip.comment = comment  # Setting the ZIP file comment

    def add_and_sign_file(self, zip_file, file_path):
        # Add file to zip
        zip_file.write(file_path, arcname=os.path.basename(file_path))

        # Sign file's content
        with open(file_path, 'rb') as f:
            content = f.read()
            signature = self.private_key.sign(
                content,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            # Optionally, write the signature to the ZIP as well
            signature_file_path = file_path + '.sig'
            with zip_file.open(signature_file_path, 'w') as sig_file:
                sig_file.write(signature)
