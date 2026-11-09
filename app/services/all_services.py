from app.schemas.all_schemas import RESERVED_PATHS

# For generating short_code
import secrets
import string

def generate_short_code() -> str:
    ch = string.ascii_letters + string.digits
    while True:
        code = "".join(secrets.choice(ch) for _ in range(8))
        if code.lower() not in RESERVED_PATHS:
            return code


# For Verifying Password
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

# For token, hashing token
import hashlib 
import secrets

def hash_token(token:str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()

def generate_token():
    return secrets.token_urlsafe(32)