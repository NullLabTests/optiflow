import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from app.core.config import settings


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    h = hashlib.scrypt(password.encode(), salt=salt.encode(), n=16384, r=8, p=1, dklen=64)
    return f"scrypt:{salt}:{h.hex()}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    parts = hashed_password.split(":")
    if len(parts) != 3 or parts[0] != "scrypt":
        return False
    _, salt, expected = parts
    h = hashlib.scrypt(plain_password.encode(), salt=salt.encode(), n=16384, r=8, p=1, dklen=64)
    return h.hex() == expected


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def decode_access_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except JWTError:
        return None
