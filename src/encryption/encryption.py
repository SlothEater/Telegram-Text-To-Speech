import os
from cryptography.fernet import Fernet


def generate_key():
    """
    Generate a new encryption key and store it in an environment variable.
    """
    key = Fernet.generate_key()
    os.environ["ENCRYPTION_KEY"] = key.decode()


def get_encryption_key() -> str:
    """
    Retrieve the encryption key from the environment variable.

    Returns:
        str: The encryption key.
    """
    return os.environ.get("ENCRYPTION_KEY")


def encrypt_key(api_key) -> bytes:
    """
    Encrypt the API key using the encryption key.

    Parameters:
        api_key (str): The API key to encrypt.

    Returns:
        bytes: The encrypted API key.
    """
    key = get_encryption_key()
    if not key:
        raise ValueError("Encryption key not found.")

    fernet = Fernet(key.encode())
    encrypted_key = fernet.encrypt(api_key.encode())
    return encrypted_key


def decrypt_key(encrypted_key) -> str:
    """
    Decrypt the encrypted key using the encryption key.

    Parameters:
        encrypted_key (bytes): The encrypted key to decrypt.

    Returns:
        str: The decrypted key.
    """
    key = get_encryption_key()
    if not key:
        raise ValueError("Encryption key not found.")

    fernet = Fernet(key.encode())
    decrypted_key = fernet.decrypt(encrypted_key).decode()
    return decrypted_key


# Check if the encryption key is stored in the environment variable, if not,
# generate a new key
if not get_encryption_key():
    generate_key()
