import secrets
import string

def generate_short_code() -> str:
    ch = string.ascii_letters + string.digits
    return "".join(secrets.choice(ch) for _ in range(8))


from fastapi import HTTPException, status
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHashError

ph = PasswordHasher()

def hash_password(password: str) -> str:
    return ph.hash(password)

def verify_password(password_hash, password):
    try:
        return ph.verify(password_hash, password)
    except VerifyMismatchError:
        return False

import hashlib 
import secrets

def hash_token(token:str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()

def generate_token():
    return secrets.token_urlsafe(32)

def verify_hash():
    return None