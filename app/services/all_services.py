import secrets
import string

def generate_short_code() -> str:
    ch = string.ascii_letters + string.digits
    return "".join(secrets.choice(ch) for _ in range(8))


from argon2 import PasswordHasher
password_hasher = PasswordHasher()

def hash_password(password: str) -> str:
    return password_hasher.hash(password)