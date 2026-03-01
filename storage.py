import os
from .config import FERNET


def encrypt_file(file_path: str):
    if not os.path.exists(file_path):
        return False

    with open(file_path, "rb") as f:
        data = f.read()

    encrypted_data = FERNET.encrypt(data)

    with open(file_path, "wb") as f:
        f.write(encrypted_data)

    return True


def decrypt_file(file_path: str):
    if not os.path.exists(file_path):
        return False

    with open(file_path, "rb") as f:
        data = f.read()

    decrypted_data = FERNET.decrypt(data)

    with open(file_path, "wb") as f:
        f.write(decrypted_data)

    return True