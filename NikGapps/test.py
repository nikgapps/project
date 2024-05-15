# from cryptography.hazmat.primitives.asymmetric import rsa
# from cryptography.hazmat.primitives import serialization
#
# # Generate a private key
# private_key = rsa.generate_private_key(
#     public_exponent=65537,
#     key_size=2048,
# )
#
# # Serialize the private key to PEM format
# pem = private_key.private_bytes(
#     encoding=serialization.Encoding.PEM,
#     format=serialization.PrivateFormat.TraditionalOpenSSL,
#     encryption_algorithm=serialization.NoEncryption()
# )
#
# # Write the PEM file to disk
# with open('private_key.pem', 'wb') as pem_file:
#     pem_file.write(pem)
from NikGapps.helper.web.Requests import Requests

print(Requests.get_package_details())
