"""Password hashing utilities using SHA-256 with salt."""
import hashlib
import secrets


def hash_password(password: str) -> str:
    """Hash a plain text password using SHA-256 with a random salt.
    
    Note: For production environments, consider using bcrypt or argon2
    with proper library support for your Python version.
    """
    salt = secrets.token_hex(16)
    password_hash = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"{salt}${password_hash}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain text password against a hashed password."""
    try:
        salt, stored_hash = hashed_password.split('$', 1)
        password_hash = hashlib.sha256((salt + plain_password).encode()).hexdigest()
        return password_hash == stored_hash
    except (ValueError, AttributeError):
        return False
