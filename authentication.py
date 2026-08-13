from datetime import datetime
from database import get_connection
from security import hash_password, verify_password

def register_user(username, password):
    username = username.strip()
    if not username or len(password) < 6:
        return False, "Username is required and password must be at least 6 characters."

    try:
        with get_connection() as conn:
            conn.execute(
                "INSERT INTO users(username,password_hash,role,created_at) VALUES(?,?,?,?)",
                (username, hash_password(password), "customer",
                 datetime.now().isoformat(timespec="seconds"))
            )
        return True, "Registration successful."
    except Exception:
        return False, "Username already exists."

def login(username, password):
    with get_connection() as conn:
        user = conn.execute(
            "SELECT * FROM users WHERE username = ?", (username.strip(),)
        ).fetchone()

    if user and verify_password(password, user["password_hash"]):
        return user
    return None
