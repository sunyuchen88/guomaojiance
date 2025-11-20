from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import hashlib
from app.config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.

    Args:
        plain_password: The plain text password to verify
        hashed_password: The hashed password to compare against

    Returns:
        True if passwords match, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt.

    Args:
        password: The plain text password to hash

    Returns:
        The hashed password
    """
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.

    Args:
        data: The data to encode in the token (usually {'sub': username})
        expires_delta: Optional expiration time delta

    Returns:
        The encoded JWT token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decode and verify a JWT access token.

    Args:
        token: The JWT token to decode

    Returns:
        The decoded token payload if valid, None otherwise
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        return None


def calculate_md5_signature(params: dict, secret: str) -> str:
    """
    Calculate MD5 signature for client API authentication.

    Args:
        params: Dictionary of parameters to sign
        secret: The secret key for signing

    Returns:
        The MD5 signature as a hex string
    """
    # Sort parameters by key
    sorted_params = sorted(params.items())

    # Concatenate key=value pairs
    sign_str = "&".join([f"{k}={v}" for k, v in sorted_params if v is not None])

    # Append secret
    sign_str += f"&key={secret}"

    # Calculate MD5
    md5_hash = hashlib.md5(sign_str.encode('utf-8')).hexdigest()

    return md5_hash.upper()
