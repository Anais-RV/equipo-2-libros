"""
🦄 AUTH - Seguridad (Hashing + JWT)

hash_password() → bcrypt
verify_password() → verificar contraseña
create_access_token() → generar JWT
verify_token() → validar JWT
"""

import os
from datetime import datetime, timedelta
from typing import Optional

# XXX TODO: from passlib.context import CryptContext
# XXX TODO: from jose import JWTError, jwt

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440

# XXX TODO: pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """XXX TODO: return pwd_context.hash(password)"""
    pass


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """XXX TODO: return pwd_context.verify(plain_password, hashed_password)"""
    pass


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """XXX TODO: Implementar JWT encoding"""
    pass


def verify_token(token: str) -> Optional[str]:
    """XXX TODO: Implementar JWT decoding, retornar email"""
    pass
