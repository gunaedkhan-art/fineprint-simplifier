# auth.py - Secure authentication module

import os
import bcrypt
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
import secrets

# Security configuration
SECRET_KEY = os.environ.get("JWT_SECRET_KEY", secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("JWT_EXPIRE_MINUTES", "60"))

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer token scheme
security = HTTPBearer()

class AuthManager:
    """Secure authentication manager with JWT tokens and bcrypt hashing"""
    
    def __init__(self):
        self.secret_key = SECRET_KEY
        self.algorithm = ALGORITHM
        self.token_expire_minutes = ACCESS_TOKEN_EXPIRE_MINUTES
    
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt"""
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.token_expire_minutes)
        
        to_encode.update({"exp": expire, "iat": datetime.utcnow()})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode a JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    def authenticate_admin(self, username: str, password: str) -> Optional[str]:
        """Authenticate admin user and return JWT token if valid"""
        # Get admin credentials from environment
        admin_username = os.environ.get("ADMIN_USERNAME", "admin")
        admin_password_hash = os.environ.get("ADMIN_PASSWORD_HASH")
        
        # If no hash is set, use the plain password (for initial setup)
        if not admin_password_hash:
            admin_plain_password = os.environ.get("ADMIN_PASSWORD", "admin123")
            if username == admin_username and password == admin_plain_password:
                # Create token for valid credentials
                token_data = {
                    "sub": username,
                    "role": "admin",
                    "type": "access_token"
                }
                return self.create_access_token(token_data)
            return None
        
        # Verify against hashed password
        if username == admin_username and self.verify_password(password, admin_password_hash):
            token_data = {
                "sub": username,
                "role": "admin",
                "type": "access_token"
            }
            return self.create_access_token(token_data)
        
        return None

# Global auth manager instance
auth_manager = AuthManager()

def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Dependency to get current authenticated admin user"""
    token = credentials.credentials
    payload = auth_manager.verify_token(token)
    
    username = payload.get("sub")
    role = payload.get("role")
    
    if username is None or role != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return {"username": username, "role": role, "payload": payload}

def create_admin_password_hash(password: str) -> str:
    """Utility function to create a password hash for admin setup"""
    return auth_manager.hash_password(password)

# Rate limiting setup (will be implemented in next step)
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)

def get_rate_limiter():
    """Get the rate limiter instance"""
    return limiter
