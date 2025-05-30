from cryptography.fernet import Fernet
import os

KEY_FILE = "crypto.key"

def generate_key():
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as f:
        f.write(key)

def load_key():
    if not os.path.exists(KEY_FILE):
        generate_key()
    with open(KEY_FILE, "rb") as f:
        return f.read()

def encrypt_file(file_path):
    key = load_key()
    fernet = Fernet(key)

    with open(file_path, "rb") as f:
        data = f.read()

    encrypted = fernet.encrypt(data)

    encrypted_path = file_path + ".enc"
    with open(encrypted_path, "wb") as f:
        f.write(encrypted)

    return encrypted_path

def decrypt_file(encrypted_path):
    key = load_key()
    fernet = Fernet(key)

    with open(encrypted_path, "rb") as f:
        encrypted_data = f.read()

    decrypted_data = fernet.decrypt(encrypted_data)

    decrypted_path = encrypted_path.replace(".enc", "")
    with open(decrypted_path, "wb") as f:
        f.write(decrypted_data)

    return decrypted_path
