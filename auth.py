# auth.py - Authentication and session management

import os
import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Dict
from fastapi import HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends

# JWT Configuration
SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 7 * 24 * 60  # 7 days (more secure)

# Security scheme
security = HTTPBearer()

class AuthManager:
    def __init__(self):
        self.secret_key = SECRET_KEY
        self.algorithm = ALGORITHM
    
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """Verify and decode a JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.JWTError:
            return None
    
    def create_password_reset_token(self, email: str, expires_minutes: int = 30) -> str:
        """Create a password reset token that expires in 30 minutes"""
        expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
        to_encode = {
            "sub": email,
            "type": "password_reset",
            "exp": expire
        }
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_password_reset_token(self, token: str) -> Optional[str]:
        """Verify password reset token and return email if valid"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            if payload.get("type") != "password_reset":
                return None
            return payload.get("sub")  # Returns email
        except jwt.ExpiredSignatureError:
            return None
        except jwt.JWTError:
            return None
    
    def get_current_user(self, credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict:
        """Get current user from JWT token"""
        token = credentials.credentials
        payload = self.verify_token(token)
        
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return {"user_id": user_id, "email": payload.get("email")}

# Global auth manager instance
auth_manager = AuthManager()

# Admin authentication functions
def get_current_admin(request: Request) -> Optional[Dict]:
    """Get current admin user from request"""
    try:
        # Check for admin session in cookies
        admin_session = request.cookies.get("admin_session")
        if not admin_session:
            return None
        
        # Verify admin session
        payload = auth_manager.verify_token(admin_session)
        if payload and payload.get("admin") == True:
            return payload
        return None
    except Exception:
        return None

def create_admin_password_hash(password: str) -> str:
    """Create a password hash for admin"""
    return auth_manager.hash_password(password)

# Dependency for getting current user
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    return auth_manager.get_current_user(credentials)

# Optional dependency for getting current user (returns None if not authenticated)
async def get_current_user_optional(request: Request) -> Optional[Dict]:
    """Get current user if authenticated, otherwise return None"""
    try:
        # Try to get token from Authorization header
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            payload = auth_manager.verify_token(token)
            if payload:
                return {"user_id": payload.get("sub"), "email": payload.get("email")}
    except:
        pass
    
    # Try to get token from cookies
    try:
        token = request.cookies.get("access_token")
        if token:
            payload = auth_manager.verify_token(token)
            if payload:
                return {"user_id": payload.get("sub"), "email": payload.get("email")}
    except:
        pass
    
    return None