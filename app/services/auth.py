from datetime import datetime, timedelta
from typing import Union, Any
from jose import jwt, JWTError
from passlib.context import CryptContext
from app.core.config import settings
import secrets

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    """Create JWT access token"""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode = {"exp": expire, "sub": str(subject), "type": "access"}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_refresh_token(subject: Union[str, Any]) -> str:
    """Create JWT refresh token (valid for 7 days)"""
    expire = datetime.utcnow() + timedelta(days=7)
    to_encode = {"exp": expire, "sub": str(subject), "type": "refresh"}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_password_reset_token(email: str) -> str:
    """Create password reset token (valid for 1 hour)"""
    expire = datetime.utcnow() + timedelta(hours=1)
    to_encode = {"exp": expire, "email": email, "type": "password_reset"}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_email_verification_token(email: str) -> str:
    """Create email verification token (valid for 24 hours)"""
    expire = datetime.utcnow() + timedelta(hours=24)
    to_encode = {"exp": expire, "email": email, "type": "email_verification"}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def verify_token(token: str, expected_type: str = "access") -> Union[str, None]:
    """Verify JWT token and return user ID"""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        
        token_type = payload.get("type")
        if token_type != expected_type:
            return None
            
        if expected_type == "access":
            user_id: str = payload.get("sub")
            return user_id
        elif expected_type == "refresh":
            user_id: str = payload.get("sub")
            return user_id
        elif expected_type == "password_reset":
            email: str = payload.get("email")
            return email
        elif expected_type == "email_verification":
            email: str = payload.get("email")
            return email
            
        return None
    except JWTError:
        return None

def generate_secure_token() -> str:
    """Generate a secure random token"""
    return secrets.token_urlsafe(32)
