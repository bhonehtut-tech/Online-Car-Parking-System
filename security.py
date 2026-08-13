import hashlib
import hmac
import secrets

def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), salt.encode(), 120_000
    ).hex()
    return f"{salt}${digest}"

def verify_password(password: str, stored_hash: str) -> bool:
    try:
        salt, expected = stored_hash.split("$", 1)
        actual = hashlib.pbkdf2_hmac(
            "sha256", password.encode(), salt.encode(), 120_000
        ).hex()
        return hmac.compare_digest(actual, expected)
    except ValueError:
        return False

def require_role(user, *allowed_roles):
    if not user or user["role"] not in allowed_roles:
        raise PermissionError("You do not have permission for this operation.")
