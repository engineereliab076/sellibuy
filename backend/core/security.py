"""Security utilities: password hashing and JWT encode/decode.

Raises jose.JWTError on invalid tokens; callers are responsible for
translating that into HTTP responses.
"""

from datetime import UTC, datetime, timedelta
from typing import Any, cast

from jose import jwt
from passlib.context import CryptContext

from core.config import settings

_ALGORITHM = "HS256"

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _parse_expiry(value: str) -> timedelta:
    """Convert an expiry string (e.g. '15m', '1h', '30d') to a timedelta."""
    unit = value[-1]
    amount = int(value[:-1])
    match unit:
        case "m":
            return timedelta(minutes=amount)
        case "h":
            return timedelta(hours=amount)
        case "d":
            return timedelta(days=amount)
        case _:
            raise ValueError(f"Unsupported expiry unit: '{unit}' in '{value}'")


def _build_payload(
    subject: str,
    token_type: str,
    token_version: int,
    expiry: timedelta,
    **extra: object,
) -> dict:
    now = datetime.now(UTC)
    return {
        "sub": subject,
        "type": token_type,
        "version": token_version,
        "iat": now,
        "exp": now + expiry,
        **extra,
    }


# ---------------------------------------------------------------------------
# Password hashing
# ---------------------------------------------------------------------------

def hash_password(password: str) -> str:
    """Return a bcrypt hash of *password*."""
    return cast(str, _pwd_context.hash(password))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Return True if *plain_password* matches *hashed_password*."""
    return cast(bool, _pwd_context.verify(plain_password, hashed_password))


# ---------------------------------------------------------------------------
# JWT creation
# ---------------------------------------------------------------------------

def create_access_token(subject: str, role: str, token_version: int) -> str:
    """Return a signed JWT access token."""
    payload = _build_payload(
        subject=subject,
        token_type="access",
        token_version=token_version,
        expiry=_parse_expiry(settings.JWT_ACCESS_EXPIRY),
        role=role,
    )
    return cast(str, jwt.encode(payload, settings.JWT_SECRET, algorithm=_ALGORITHM))


def create_refresh_token(subject: str, token_version: int) -> str:
    """Return a signed JWT refresh token (no role claim)."""
    payload = _build_payload(
        subject=subject,
        token_type="refresh",
        token_version=token_version,
        expiry=_parse_expiry(settings.JWT_REFRESH_EXPIRY),
    )
    return cast(str, jwt.encode(payload, settings.JWT_REFRESH_SECRET, algorithm=_ALGORITHM))


# ---------------------------------------------------------------------------
# JWT decoding
# ---------------------------------------------------------------------------

def _decode_token(token: str, secret: str, expected_type: str) -> dict[str, Any]:
    payload = cast(dict[str, Any], jwt.decode(token, secret, algorithms=[_ALGORITHM]))
    if payload.get("type") != expected_type:
        raise ValueError(f"Invalid token type: expected {expected_type}")
    return payload


def decode_access_token(token: str) -> dict:
    """Decode and verify an access token. Raises jose.JWTError or ValueError on failure."""
    return _decode_token(token, settings.JWT_SECRET, "access")


def decode_refresh_token(token: str) -> dict:
    """Decode and verify a refresh token. Raises jose.JWTError or ValueError on failure."""
    return _decode_token(token, settings.JWT_REFRESH_SECRET, "refresh")
