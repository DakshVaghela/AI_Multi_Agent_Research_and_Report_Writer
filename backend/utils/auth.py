import hashlib
import os


def hash_password(password: str) -> str:
    """
    Securely hash a password using PBKDF2 (SHA-256) with a random salt.
    Returns the salt and hash concatenated with a colon (salt:hash).
    """
    salt = os.urandom(16)
    key = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        100000,
    )
    return f"{salt.hex()}:{key.hex()}"


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.
    """
    try:
        salt_hex, key_hex = hashed_password.split(":")
        salt = bytes.fromhex(salt_hex)
        key = bytes.fromhex(key_hex)
    except (ValueError, TypeError):
        return False

    new_key = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        100000,
    )
    return key == new_key
