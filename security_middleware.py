# security_middleware.py - Security middleware and headers

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import RedirectResponse
import os
import time
from typing import Dict, Any

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Security headers
        security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
            "Content-Security-Policy": (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' https://js.stripe.com; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self'; "
                "connect-src 'self' https://api.stripe.com; "
                "frame-src https://js.stripe.com;"
            )
        }
        
        # Add Strict-Transport-Security for HTTPS
        if request.url.scheme == "https":
            security_headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # Add headers to response
        for header, value in security_headers.items():
            response.headers[header] = value
        
        return response

class HTTPSRedirectMiddleware(BaseHTTPMiddleware):
    """Redirect HTTP to HTTPS in production"""
    
    def __init__(self, app, force_https: bool = None):
        super().__init__(app)
        self.force_https = force_https if force_https is not None else os.environ.get("FORCE_HTTPS", "false").lower() == "true"
    
    async def dispatch(self, request: Request, call_next):
        # Only redirect in production and if force_https is enabled
        if self.force_https and request.url.scheme == "http":
            https_url = request.url.replace(scheme="https")
            return RedirectResponse(url=str(https_url), status_code=301)
        
        return await call_next(request)

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory rate limiting middleware"""
    
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, list] = {}
    
    def get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
        # Check for forwarded headers (for reverse proxies)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    async def dispatch(self, request: Request, call_next):
        client_ip = self.get_client_ip(request)
        current_time = time.time()
        
        # Clean old requests (older than 1 minute)
        if client_ip in self.requests:
            self.requests[client_ip] = [
                req_time for req_time in self.requests[client_ip]
                if current_time - req_time < 60
            ]
        else:
            self.requests[client_ip] = []
        
        # Check rate limit
        if len(self.requests[client_ip]) >= self.requests_per_minute:
            return Response(
                content="Rate limit exceeded. Please try again later.",
                status_code=429,
                headers={"Retry-After": "60"}
            )
        
        # Add current request
        self.requests[client_ip].append(current_time)
        
        return await call_next(request)

class AdminRateLimitMiddleware(BaseHTTPMiddleware):
    """Enhanced rate limiting for admin endpoints"""
    
    def __init__(self, app, admin_requests_per_minute: int = 30):
        super().__init__(app)
        self.admin_requests_per_minute = admin_requests_per_minute
        self.admin_requests: Dict[str, list] = {}
    
    def get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    async def dispatch(self, request: Request, call_next):
        # Only apply to admin routes
        if not request.url.path.startswith("/admin"):
            return await call_next(request)
        
        client_ip = self.get_client_ip(request)
        current_time = time.time()
        
        # Clean old requests
        if client_ip in self.admin_requests:
            self.admin_requests[client_ip] = [
                req_time for req_time in self.admin_requests[client_ip]
                if current_time - req_time < 60
            ]
        else:
            self.admin_requests[client_ip] = []
        
        # Check rate limit
        if len(self.admin_requests[client_ip]) >= self.admin_requests_per_minute:
            return Response(
                content="Admin rate limit exceeded. Please try again later.",
                status_code=429,
                headers={"Retry-After": "60"}
            )
        
        # Add current request
        self.admin_requests[client_ip].append(current_time)
        
        return await call_next(request)

def setup_security_middleware(app):
    """Setup all security middleware"""
    # Add security headers
    app.add_middleware(SecurityHeadersMiddleware)
    
    # Add HTTPS redirect (if enabled)
    app.add_middleware(HTTPSRedirectMiddleware)
    
    # Add general rate limiting
    app.add_middleware(RateLimitMiddleware, requests_per_minute=120)
    
    # Add admin-specific rate limiting
    app.add_middleware(AdminRateLimitMiddleware, admin_requests_per_minute=30)
