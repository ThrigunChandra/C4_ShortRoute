import secrets
import string

def generate_short_code() -> str:
    ch = string.ascii_letters + string.digits
    return "".join(secrets.choice(ch) for _ in range(8))