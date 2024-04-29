import os
import zipfile
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.backends import default_backend
from base64 import b64encode
import hashlib


class Zip:
    RSAFileName = "META-INF/Nik.RSA"
    SFFileName = "META-INF/Nik.SF"
    ManifestFileName = "META-INF/MANIFEST.MF"
    DigitalMessage = "Author:- Nikhil Menghani (Nikhil @ Xda-developers.com)"
    SignatureVersion = "1.0"
    ManifestVersion = "1.0"
    CreatedBy = "Nikhil @ XDA"

    def __init__(self, name, sign=False, private_key_path=None, comment=DigitalMessage):
        directory = os.path.dirname(name)
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

        self.zipObj = zipfile.ZipFile(name, 'w', compression=zipfile.ZIP_DEFLATED)
        self.comment = comment.encode()
        self.sign = sign
        if self.sign:
            if private_key_path is None:
                raise ValueError("Private key path must be provided for signing.")
            self.private_key = self.load_private_key(private_key_path)
            self.signatures = {}
            self.manifest_digests = {}

    def load_private_key(self, file_path):
        with open(file_path, 'rb') as key_file:
            return load_pem_private_key(
                key_file.read(),
                password=None,
                backend=default_backend()
            )

    def add_file(self, filename, zippath=None):
        if zippath is None:
            zippath = filename
        self.zipObj.write(filename, zippath)
        if self.sign:
            self.sign_content(filename, zippath)

    def add_string(self, text, zippath):
        text = text.replace('\r\n', '\n')
        self.zipObj.writestr(zippath, text)
        if self.sign:
            self.sign_content_string(text, zippath)

    def sign_content(self, filename, zippath):
        with open(filename, 'rb') as f:
            content = f.read()
        self.process_signature(content, zippath)

    def sign_content_string(self, text, zippath):
        content = text.encode()
        self.process_signature(content, zippath)

    def process_signature(self, content, zippath):
        digest = hashlib.sha256(content).digest()
        self.manifest_digests[zippath] = b64encode(digest).decode('utf-8')
        signature = self.private_key.sign(
            digest,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        self.signatures[zippath] = b64encode(signature).decode('utf-8')
        # self.zipObj.writestr(zippath + '.sig', signature)

    def generate_manifest_and_signature_files(self):
        manifest_content = f"Manifest-Version: {self.ManifestVersion}\nCreated-By: {self.CreatedBy}\n"
        for filename, digest in self.manifest_digests.items():
            manifest_content += f"Name: {filename}\nSHA-256-Digest: {digest}\n"
        self.zipObj.writestr(self.ManifestFileName, manifest_content)

        sf_content = f"Signature-Version: {self.SignatureVersion}\nCreated-By: {self.CreatedBy}\n"
        self.zipObj.writestr(self.SFFileName, sf_content)

        rsa_content = f"Digital-Message: {self.DigitalMessage}\nSignatures:\n"
        for filename, signature in self.signatures.items():
            rsa_content += f"{filename}: {signature}\n"
        self.zipObj.writestr(self.RSAFileName, rsa_content)

    def close(self):
        if self.sign:
            self.generate_manifest_and_signature_files()
            self.zipObj.comment = self.comment
        self.zipObj.close()
