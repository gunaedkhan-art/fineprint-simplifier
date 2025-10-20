# smallprintchecker/main.py

from fastapi import FastAPI, UploadFile, File, Request, Form, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse, Response, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBearer
from collections import defaultdict
from pdf_parser import extract_text_from_pdf
from preprocess_text import preprocess_text
from matcher import find_risks_in_text
from analyzer import analyze_pdf, analyze_text_content
import os
import json
import re
from datetime import datetime, timedelta
import time
import pickle
from collections import defaultdict

# Load environment variables from .env file if it exists

# Visitor tracking for fair use limits
VISITOR_UPLOADS_FILE = "visitor_uploads.pkl"

def get_visitor_ip(request: Request) -> str:
    """Get visitor IP address"""
    # Try to get real IP from headers (for proxies)
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip
    
    # Fallback to client host
    return request.client.host if request.client else "unknown"

def get_visitor_uploads_today(request: Request) -> int:
    """Get number of uploads by this visitor today"""
    visitor_ip = get_visitor_ip(request)
    today = datetime.now().strftime("%Y-%m-%d")
    
    try:
        # Load existing visitor data
        if os.path.exists(VISITOR_UPLOADS_FILE):
            with open(VISITOR_UPLOADS_FILE, 'rb') as f:
                visitor_data = pickle.load(f)
        else:
            visitor_data = {}
        
        # Get uploads for this IP today
        ip_data = visitor_data.get(visitor_ip, {})
        return ip_data.get(today, 0)
        
    except Exception as e:
        print(f"Error loading visitor upload data: {e}")
        import traceback
        traceback.print_exc()
        return 0

def record_visitor_upload(request: Request):
    """Record a visitor upload for fair use tracking"""
    visitor_ip = get_visitor_ip(request)
    today = datetime.now().strftime("%Y-%m-%d")
    
    try:
        # Load existing visitor data
        if os.path.exists(VISITOR_UPLOADS_FILE):
            with open(VISITOR_UPLOADS_FILE, 'rb') as f:
                visitor_data = pickle.load(f)
        else:
            visitor_data = {}
        
        # Initialize IP data if needed
        if visitor_ip not in visitor_data:
            visitor_data[visitor_ip] = {}
        
        # Increment upload count for today
        visitor_data[visitor_ip][today] = visitor_data[visitor_ip].get(today, 0) + 1
        
        # Save updated data
        with open(VISITOR_UPLOADS_FILE, 'wb') as f:
            pickle.dump(visitor_data, f)
        
        print(f"📊 Recorded visitor upload: {visitor_ip} - {visitor_data[visitor_ip][today]} uploads today")
        
    except Exception as e:
        print(f"Error recording visitor upload: {e}")
        import traceback
        traceback.print_exc()

def cleanup_old_visitor_data():
    """Clean up visitor data older than 30 days"""
    try:
        if not os.path.exists(VISITOR_UPLOADS_FILE):
            return
        
        with open(VISITOR_UPLOADS_FILE, 'rb') as f:
            visitor_data = pickle.load(f)
        
        cutoff_date = datetime.now() - timedelta(days=30)
        cutoff_str = cutoff_date.strftime("%Y-%m-%d")
        
        # Clean up old data
        for ip in list(visitor_data.keys()):
            ip_data = visitor_data[ip]
            for date_str in list(ip_data.keys()):
                if date_str < cutoff_str:
                    del ip_data[date_str]
            
            # Remove IP if no data left
            if not ip_data:
                del visitor_data[ip]
        
        # Save cleaned data
        with open(VISITOR_UPLOADS_FILE, 'wb') as f:
            pickle.dump(visitor_data, f)
        
        print(f"🧹 Cleaned up visitor data older than {cutoff_str}")
        
    except Exception as e:
        print(f"Error cleaning up visitor data: {e}")
        import traceback
        traceback.print_exc()

try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✓ Environment variables loaded from .env file")
except ImportError:
    print("⚠ python-dotenv not installed, using system environment variables only")
except Exception as e:
    print(f"⚠ Error loading .env file: {e}")

# Test custom module imports with error handling
try:
    from core_patterns import RISK_PATTERNS, GOOD_PATTERNS  # live update support
    print("✓ core_patterns imported successfully")
except Exception as e:
    print(f"✗ core_patterns import failed: {e}")
    RISK_PATTERNS = {}
    GOOD_PATTERNS = {}

try:
    from user_management_db import UserManager
    user_manager = UserManager()
    print("✓ user_management (database-backed) imported successfully")
except Exception as e:
    print(f"⚠ Database-backed user_management failed: {e}")
    try:
        # Fallback to file-based user management
        from user_management import user_manager as file_user_manager
        user_manager = file_user_manager
        print("✓ Fallback to file-based user_management successful")
    except Exception as e2:
        print(f"✗ Both user_management systems failed: {e2}")
        user_manager = None

try:
    from auth import auth_manager, get_current_user_optional
    print("✓ auth imported successfully")
except Exception as e:
    print(f"✗ auth import failed: {e}")
    auth_manager = None
    get_current_user_optional = None

try:
    from pricing_config import FREE_TIER_LIMITS, PAID_TIER_FEATURES, FEATURE_DESCRIPTIONS, PRICING
    print("✓ pricing_config imported successfully")
except Exception as e:
    print(f"✗ pricing_config import failed: {e}")
    FREE_TIER_LIMITS = {}
    PAID_TIER_FEATURES = []
    FEATURE_DESCRIPTIONS = {}
    PRICING = {}

try:
    from admin import router as admin_router
    print("✓ admin router imported successfully")
except Exception as e:
    print(f"✗ admin router import failed: {e}")
    admin_router = None

try:
    from security_middleware import setup_security_middleware
    print("✓ security middleware imported successfully")
except Exception as e:
    print(f"✗ security middleware import failed: {e}")
    setup_security_middleware = None

try:
    from sitemap_generator import get_sitemap_xml, get_robots_txt, update_base_url
    print("✓ sitemap generator imported successfully")
except Exception as e:
    print(f"✗ sitemap generator import failed: {e}")
    get_sitemap_xml = None
    get_robots_txt = None
    update_base_url = None

try:
    from stripe_integration import stripe_manager, create_payment_session, handle_successful_payment
    print("✓ stripe integration imported successfully")
except Exception as e:
    print(f"✗ stripe integration import failed: {e}")
    stripe_manager = None

try:
    from email_service import send_welcome_email, send_password_reset_email, send_password_changed_email
    print("✓ email service imported successfully")
except Exception as e:
    print(f"✗ email service import failed: {e}")
    send_welcome_email = None
    send_password_reset_email = None
    send_password_changed_email = None

app = FastAPI()

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app):
    """Handle startup and shutdown events"""
    print("🚀 Application starting up...")
    try:
        print("✓ FastAPI app created successfully")
        
        # Initialize database
        try:
            from database import init_database
            init_database()
            print("✓ Database initialized successfully")
        except Exception as e:
            print(f"⚠ Database initialization warning: {e}")
            print("ℹ️ App will continue with file-based storage as fallback")
            # Continue startup even if database fails (fallback to file-based)
        
        # Clean up old visitor data
        cleanup_old_visitor_data()
        
    except Exception as e:
        print(f"✗ Startup error: {e}")
    yield
    print("🛑 Application shutting down...")

app = FastAPI(lifespan=lifespan)

# Rate limiting storage
login_attempts = defaultdict(list)
MAX_LOGIN_ATTEMPTS = 5
LOGIN_WINDOW = 300  # 5 minutes

def check_rate_limit(ip_address: str) -> bool:
    """Check if IP has exceeded login attempt rate limit"""
    current_time = time.time()
    
    # Clean old attempts
    login_attempts[ip_address] = [
        attempt_time for attempt_time in login_attempts[ip_address]
        if current_time - attempt_time < LOGIN_WINDOW
    ]
    
    # Check if limit exceeded
    if len(login_attempts[ip_address]) >= MAX_LOGIN_ATTEMPTS:
        return False
    
    return True

def record_login_attempt(ip_address: str):
    """Record a login attempt for rate limiting"""
    current_time = time.time()
    login_attempts[ip_address].append(current_time)

def get_client_ip(request: Request) -> str:
    """Get client IP address for rate limiting"""
    # Check for forwarded IP (behind proxy)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    # Check for real IP
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Fallback to direct connection
    return request.client.host if request.client else "unknown"

# Setup security middleware
if setup_security_middleware:
    setup_security_middleware(app)
    print("✓ Security middleware configured")

# Serve static files (CSS, JS)
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
    print("✓ Static files mounted successfully")
except Exception as e:
    print(f"✗ Static files mounting failed: {e}")

# Set up Jinja2 templating
try:
    templates = Jinja2Templates(directory="templates")
    print("✓ Jinja2 templates setup successfully")
except Exception as e:
    print(f"✗ Jinja2 templates setup failed: {e}")
    templates = None

CUSTOM_FILE = "custom_patterns.json"
PENDING_FILE = "pending_patterns.json"


# -------------------------
# Helpers for JSON storage
# -------------------------
def load_json_file(filepath, default=None):
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            return json.load(f)
    return default or {}


def save_json_file(filepath, data):
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)


def load_custom_patterns():
    return load_json_file(CUSTOM_FILE, {"risks": {}, "good_points": {}})


def save_custom_patterns(data):
    save_json_file(CUSTOM_FILE, data)


def load_pending_patterns():
    return load_json_file(PENDING_FILE, {"risks": {}, "good_points": {}})


def save_pending_patterns(data):
    save_json_file(PENDING_FILE, data)


def load_pattern_descriptions():
    """Load pattern descriptions from JSON file"""
    return load_json_file('pattern_descriptions.json', {})


def save_pattern_descriptions(descriptions):
    """Save pattern descriptions to JSON file"""
    save_json_file('pattern_descriptions.json', descriptions)


# -------------------------
# Routes
# -------------------------
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    # Get current user for server-side rendering
    current_user = None
    user_authenticated = False
    
    if get_current_user_optional:
        try:
            current_user = await get_current_user_optional(request)
            if current_user:
                user_authenticated = True
                # Get user usage data
                user_usage = user_manager.get_user_usage(current_user.get("user_id"))
                if user_usage:
                    current_user["usage"] = user_usage
        except Exception:
            pass
    
    return templates.TemplateResponse("home.html", {
        "request": request,
        "user_authenticated": user_authenticated,
        "user": current_user
    })

@app.get("/upload", response_class=HTMLResponse)
async def upload_page(request: Request):
    # Get current user for server-side rendering
    current_user = None
    user_authenticated = False
    
    if get_current_user_optional:
        try:
            current_user = await get_current_user_optional(request)
            if current_user:
                user_authenticated = True
                # Get user usage data
                user_usage = user_manager.get_user_usage(current_user.get("user_id"))
                if user_usage:
                    current_user["usage"] = user_usage
        except Exception:
            pass
    
    return templates.TemplateResponse("upload.html", {
        "request": request,
        "user_authenticated": user_authenticated,
        "user": current_user
    })

@app.get("/analysis", response_class=HTMLResponse)
async def analysis_page(request: Request):
    # Check if user is authenticated
    current_user = None
    user_authenticated = False
    
    if get_current_user_optional:
        try:
            current_user = await get_current_user_optional(request)
            if current_user:
                user_authenticated = True
                # Get user usage data
                user_usage = user_manager.get_user_usage(current_user.get("user_id"))
                if user_usage:
                    current_user["usage"] = user_usage
        except Exception:
            pass
    
    if not user_authenticated:
        return RedirectResponse(url="/login", status_code=302)
    
    return templates.TemplateResponse("analysis.html", {
        "request": request,
        "user_authenticated": user_authenticated,
        "user": current_user
    })

@app.get("/compare", response_class=HTMLResponse)
async def compare_page(request: Request):
    # Get current user for server-side rendering
    current_user = None
    user_authenticated = False
    
    if get_current_user_optional:
        try:
            current_user = await get_current_user_optional(request)
            if current_user:
                user_authenticated = True
                # Get user usage data
                user_usage = user_manager.get_user_usage(current_user.get("user_id"))
                if user_usage:
                    current_user["usage"] = user_usage
        except Exception:
            pass
    
    return templates.TemplateResponse("compare.html", {
        "request": request,
        "user_authenticated": user_authenticated,
        "user": current_user
    })

@app.get("/how-it-works", response_class=HTMLResponse)
async def how_it_works_page(request: Request):
    # Get current user for server-side rendering
    current_user = None
    user_authenticated = False
    
    if get_current_user_optional:
        try:
            current_user = await get_current_user_optional(request)
            if current_user:
                user_authenticated = True
                # Get user usage data
                user_usage = user_manager.get_user_usage(current_user.get("user_id"))
                if user_usage:
                    current_user["usage"] = user_usage
        except Exception:
            pass
    
    return templates.TemplateResponse("how-it-works.html", {
        "request": request,
        "user_authenticated": user_authenticated,
        "user": current_user
    })

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/forgot-password", response_class=HTMLResponse)
async def forgot_password_page(request: Request):
    return templates.TemplateResponse("forgot_password.html", {"request": request})

@app.get("/reset-password", response_class=HTMLResponse)
async def reset_password_page(request: Request, token: str = ""):
    return templates.TemplateResponse("reset_password.html", {"request": request, "token": token})

@app.get("/fix-account", response_class=HTMLResponse)
async def fix_account_page(request: Request):
    return templates.TemplateResponse("fix_account.html", {"request": request})

@app.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request):
    # Get current user
    current_user = None
    if get_current_user_optional:
        current_user = await get_current_user_optional(request)
    
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    
    # Get user data
    user_data = None
    if user_manager:
        user_data = user_manager.get_user(current_user["user_id"])
    
    return templates.TemplateResponse("profile.html", {
        "request": request,
        "user": current_user,
        "user_data": user_data
    })

@app.get("/subscription-management", response_class=HTMLResponse)
async def subscription_management_page(request: Request):
    # Get current user
    current_user = None
    if get_current_user_optional:
        current_user = await get_current_user_optional(request)
    
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    
    # Get user data
    user_data = None
    if user_manager:
        user_data = user_manager.get_user(current_user["user_id"])
    
    # Check if user has a paid subscription
    if not user_data or user_data.get("subscription") != "paid":
        return RedirectResponse(url="/pricing", status_code=302)
    
    return templates.TemplateResponse("subscription_management.html", {
        "request": request,
        "user": current_user,
        "user_data": user_data
    })

@app.get("/payment-success", response_class=HTMLResponse)
async def payment_success_page(request: Request):
    """Payment success page after Stripe checkout"""
    return templates.TemplateResponse("payment_success.html", {"request": request})

@app.get("/payment-error", response_class=HTMLResponse)
async def payment_error_page(request: Request):
    """Payment error page for failed payments"""
    return templates.TemplateResponse("payment_error.html", {"request": request})

@app.get("/api/upgrade-abandoners")
async def get_upgrade_abandoners():
    """Get list of users who have abandoned upgrades (for marketing)"""
    if not user_manager:
        return JSONResponse(
            content={"error": "User management not available"},
            status_code=500
        )
    
    abandoners = user_manager.get_upgrade_abandoners()
    return JSONResponse(content={
        "success": True,
        "abandoners": abandoners,
        "count": len(abandoners)
    })

@app.post("/api/track-abandonment/{user_id}")
async def track_upgrade_abandonment(user_id: str):
    """Track when a user abandons the upgrade process"""
    if not user_manager:
        return JSONResponse(
            content={"error": "User management not available"},
            status_code=500
        )
    
    try:
        user_manager.track_upgrade_abandonment(user_id)
        return JSONResponse(content={"success": True, "message": "Abandonment tracked"})
    except Exception as e:
        return JSONResponse(
            content={"error": f"Failed to track abandonment: {str(e)}"},
            status_code=500
        )


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    # Absolute minimal health check with no external dependencies
    return {"status": "healthy"}

@app.get("/admin/health")
async def admin_health_check():
    """Admin health check to verify admin routes are working"""
    return {
        "status": "healthy", 
        "admin_routes": "available",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/debug/routes")
async def debug_routes():
    """Debug endpoint to check all registered routes"""
    admin_routes = []
    all_routes = []
    
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            route_info = {
                "path": route.path,
                "methods": list(route.methods)
            }
            all_routes.append(route_info)
            
            if route.path.startswith('/admin'):
                admin_routes.append(route_info)
    
    return {
        "total_routes": len(all_routes),
        "admin_routes": len(admin_routes),
        "admin_routes_list": admin_routes,
        "all_routes": all_routes
    }

# SEO Routes
@app.get("/sitemap.xml")
async def sitemap_xml():
    """Generate dynamic XML sitemap for search engines"""
    try:
        xml_content = get_sitemap_xml()
        return Response(
            content=xml_content,
            media_type="application/xml",
            headers={"Cache-Control": "public, max-age=3600"}  # Cache for 1 hour
        )
    except Exception as e:
        return Response(
            content=f"Sitemap generation failed: {str(e)}", 
            status_code=500,
            media_type="text/plain"
        )

@app.get("/robots.txt")
async def robots_txt():
    """Generate robots.txt for search engines"""
    try:
        robots_content = get_robots_txt()
        return Response(
            content=robots_content,
            media_type="text/plain",
            headers={"Cache-Control": "public, max-age=86400"}  # Cache for 24 hours
        )
    except Exception as e:
        return Response(
            content=f"Robots.txt generation failed: {str(e)}", 
            status_code=500,
            media_type="text/plain"
        )

@app.get("/favicon.ico")
async def favicon():
    """Serve favicon"""
    from fastapi.responses import FileResponse
    return FileResponse("static/favicon.ico")

@app.get("/admin/test")
async def admin_test():
    """Simple test route to verify admin path is working"""
    return {"message": "Admin routes are working!", "timestamp": datetime.now().isoformat()}

@app.get("/ping")
async def ping():
    """Simple ping endpoint for testing"""
    return {"message": "pong"}

# Root endpoint removed - using the home page route above instead

# Include admin router if available
if admin_router:
    try:
        app.include_router(admin_router)
        print("✓ admin router included successfully")
        
        # Debug: Print admin routes
        admin_routes = [route for route in app.routes if hasattr(route, 'path') and route.path.startswith('/admin')]
        print(f"✓ {len(admin_routes)} admin routes registered:")
        for route in admin_routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                methods = ', '.join(route.methods)
                print(f"  {methods} {route.path}")
                
    except Exception as e:
        print(f"✗ admin router inclusion failed: {e}")
else:
    print("⚠ admin router not available")

@app.get("/pricing", response_class=HTMLResponse)
async def pricing_page(request: Request):
    # Get current user for server-side rendering
    current_user = None
    user_authenticated = False
    
    if get_current_user_optional:
        try:
            current_user = await get_current_user_optional(request)
            if current_user:
                user_authenticated = True
                # Get user usage data
                user_usage = user_manager.get_user_usage(current_user.get("user_id"))
                if user_usage:
                    current_user["usage"] = user_usage
        except Exception:
            pass
    
    return templates.TemplateResponse("pricing.html", {
        "request": request,
        "user_authenticated": user_authenticated,
        "user": current_user
    })


@app.get("/api/pricing")
async def get_pricing():
    """Get pricing information"""
    try:
        return {
            "free_tier": {
                "documents_per_month": FREE_TIER_LIMITS.get("documents_per_month", 3),
                "features": FREE_TIER_LIMITS.get("features", []),
                "feature_descriptions": {k: FEATURE_DESCRIPTIONS.get(k, "") for k in FREE_TIER_LIMITS.get("features", [])}
            },
            "paid_tier": {
                "features": PAID_TIER_FEATURES,
                "feature_descriptions": {k: FEATURE_DESCRIPTIONS.get(k, "") for k in PAID_TIER_FEATURES}
            },
            "pricing": PRICING
        }
    except Exception as e:
        # Fallback pricing if config fails
        return {
            "free_tier": {
                "documents_per_month": 3,
                "features": ["basic_analysis"],
                "feature_descriptions": {"basic_analysis": "Basic document analysis"}
            },
            "paid_tier": {
                "features": ["advanced_analysis", "comparison"],
                "feature_descriptions": {
                    "advanced_analysis": "Advanced analysis features",
                    "comparison": "Document comparison"
                }
            },
            "pricing": {"monthly": 9.99, "yearly": 99.99}
        }


@app.get("/api/usage/{user_id}")
async def get_usage(user_id: str):
    """Get user usage information"""
    if user_manager:
        user = user_manager.get_user(user_id)
        print(f"🔍 USAGE DEBUG: user_id={user_id}, user_found={user is not None}")
        if user:
            print(f"🔍 USAGE DEBUG: user_email={user.get('email')}, has_email={bool(user.get('email'))}")
        
        # If user doesn't exist or has no email, they're a visitor
        if not user or not user.get("email"):
            print(f"🔍 USAGE DEBUG: Returning visitor data (no email)")
            # Visitors can always upload (no limits)
            return {
                "subscription": "free",
                "email": None,
                "documents_this_month": 0,
                "total_documents": 0,
                "monthly_limit": 3,
                "can_upload": True  # Visitors can always upload
            }
        
        print(f"🔍 USAGE DEBUG: Returning authenticated user data")
        # For logged-in users, get normal usage summary
        return user_manager.get_usage_summary(user_id)
    else:
        return {"error": "User management not available"}


@app.post("/api/register")
async def register_user(request: Request):
    """Register a new user"""
    if not auth_manager or not user_manager:
        return JSONResponse(
            content={"error": "Authentication not available"},
            status_code=500
        )
    
    try:
        data = await request.json()
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")
        anonymous_user_id = data.get("anonymous_user_id")  # For merging anonymous user data
        
        if not username or not email or not password:
            return JSONResponse(
                content={"error": "Username, email and password are required"},
                status_code=400
            )
        
        # Check if user already exists by email
        existing_user = user_manager.get_user_by_email(email)
        if existing_user:
            return JSONResponse(
                content={"error": "User with this email already exists"},
                status_code=400
            )
        
        # Check if username already exists
        existing_username = user_manager.get_user_by_username(username)
        if existing_username:
            return JSONResponse(
                content={"error": "Username already taken"},
                status_code=400
            )
        
        # Hash password and create user
        password_hash = auth_manager.hash_password(password)
        
        print(f"🔧 REGISTRATION ATTEMPT: username={username}, email={email}")
        print(f"🔧 Password hash created: {bool(password_hash)}")
        
        user_id, user_data = user_manager.create_authenticated_user(username, email, password_hash)
        
        print(f"🔧 create_authenticated_user returned: user_id={user_id}, user_data keys={list(user_data.keys()) if user_data else None}")
        print(f"🔧 user_data email field: {user_data.get('email') if user_data else None}")
        
        if not user_id or not user_data:
            return JSONResponse(
                content={"error": "Failed to create user"},
                status_code=500
            )
        
        print(f"✅ REGISTRATION SUCCESS: user_id={user_id}, email={email}, username={username}")
        
        # Verify user was created successfully
        created_user = user_manager.get_user(user_id)
        if created_user:
            print(f"✅ User verification successful: email={created_user.get('email')}")
        else:
            print(f"❌ User verification failed: user not found after creation")
        
        # If there's an anonymous user ID, merge the data
        if anonymous_user_id:
            anonymous_user = user_manager.get_user(anonymous_user_id)
            if anonymous_user:
                print(f"🔄 Merging anonymous user data from {anonymous_user_id}")
                
                # Merge usage data from anonymous user
                if "usage" in anonymous_user:
                    user_data["usage"] = anonymous_user["usage"]
                
                # Merge any other relevant data
                if "documents_analyzed" in anonymous_user:
                    user_data["documents_analyzed"] = anonymous_user["documents_analyzed"]
                
                # Update the user data in the database
                user_manager.db.update_user(user_id, **user_data)
            
            # Remove the anonymous user
            user_manager.delete_user(anonymous_user_id)
        
        # Record usage for registration ONLY if there is pending visitor analysis
        # This ensures they get 1/3 usage only if they uploaded as a visitor
        # Direct registration without upload should start at 0/3 usage
        
        # Create access token
        access_token = auth_manager.create_access_token(
            data={"sub": user_id, "email": email}
        )
        
        # Send welcome email
        if send_welcome_email:
            try:
                email_result = send_welcome_email(email, username)
                if email_result.get("success"):
                    print(f"✓ Welcome email sent to {email}")
                else:
                    print(f"⚠ Welcome email failed: {email_result.get('error')}")
            except Exception as e:
                print(f"⚠ Welcome email error: {str(e)}")
        
        return JSONResponse(content={
            "success": True,
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": user_id
        })
        
    except Exception as e:
        return JSONResponse(
            content={"error": f"Registration failed: {str(e)}"},
            status_code=500
        )

@app.post("/api/login")
async def login_user(request: Request):
    """Login user with rate limiting"""
    if not auth_manager or not user_manager:
        return JSONResponse(
            content={"error": "Authentication not available"},
            status_code=500
        )
    
    # Get client IP for rate limiting
    client_ip = get_client_ip(request)
    
    # Check rate limit
    if not check_rate_limit(client_ip):
        return JSONResponse(
            content={"error": "Too many login attempts. Please try again in 5 minutes."},
            status_code=429
        )
    
    try:
        data = await request.json()
        email = data.get("email")
        password = data.get("password")
        
        if not email or not password:
            return JSONResponse(
                content={"error": "Email and password are required"},
                status_code=400
            )
        
        # Authenticate user
        user = user_manager.authenticate_user(email, password)
        if not user:
            # Record failed attempt
            record_login_attempt(client_ip)
            # Log the failed attempt for debugging
            print(f"LOGIN FAILED: Email={email}, User exists: {user_manager.get_user_by_email(email) is not None}")
            return JSONResponse(
                content={"error": "Invalid email or password"},
                status_code=401
            )
        
        # Create access token
        access_token = auth_manager.create_access_token(
            data={"sub": user["user_id"], "email": email}
        )
        
        return JSONResponse(content={
            "success": True,
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": user["user_id"],
            "usage": user_manager.get_usage_summary(user["user_id"]) if user_manager else None
        })
        
    except Exception as e:
        return JSONResponse(
            content={"error": f"Login failed: {str(e)}"},
            status_code=500
        )

@app.post("/api/record-usage")
async def record_usage(request: Request):
    """Record usage for a user (called when showing pending analysis)"""
    try:
        # Get current user
        current_user = await get_current_user_optional(request)
        if not current_user:
            return JSONResponse(
                content={"error": "Authentication required"},
                status_code=401
            )
        
        user_id = current_user.get("user_id")
        if user_manager:
            success = user_manager.record_document_upload(user_id)
            if success:
                print(f"📊 Recorded usage for user: {user_id}")
                return JSONResponse(content={"success": True})
            else:
                return JSONResponse(
                    content={"error": "Failed to record usage"},
                    status_code=500
                )
        else:
            return JSONResponse(
                content={"error": "User management not available"},
                status_code=500
            )
            
    except Exception as e:
        return JSONResponse(
            content={"error": f"Usage recording failed: {str(e)}"},
            status_code=500
        )

@app.post("/api/logout")
async def logout_user():
    """Logout user (client-side token removal)"""
    return JSONResponse(content={"success": True, "message": "Logged out successfully"})

@app.post("/api/forgot-password")
async def forgot_password(request: Request):
    """Send password reset token"""
    if not auth_manager or not user_manager:
        return JSONResponse(
            content={"error": "Authentication not available"},
            status_code=500
        )
    
    try:
        data = await request.json()
        email = data.get("email")
        
        if not email:
            return JSONResponse(
                content={"error": "Email is required"},
                status_code=400
            )
        
        # Check if user exists
        user = user_manager.get_user_by_email(email)
        
        # Always return success to prevent email enumeration
        # But only create token and send email if user exists
        if user:
            reset_token = auth_manager.create_password_reset_token(email)
            print(f"PASSWORD RESET: Token generated for {email}")
            
            # Send email if service is available
            if send_password_reset_email:
                try:
                    email_result = send_password_reset_email(email, reset_token)
                    if email_result.get("success"):
                        print(f"✓ Password reset email sent to {email}")
                    else:
                        print(f"⚠ Password reset email failed: {email_result.get('error')}")
                        # Fallback: return token in response if email fails
                        return JSONResponse(content={
                            "success": True,
                            "message": "Password reset link generated (email service unavailable).",
                            "reset_url": f"/reset-password?token={reset_token}"
                        })
                except Exception as e:
                    print(f"⚠ Password reset email error: {str(e)}")
            else:
                # Email service not available - return link in response (development mode)
                print(f"⚠ Email service not configured - returning reset link")
                return JSONResponse(content={
                    "success": True,
                    "message": "Password reset link generated (email not configured).",
                    "reset_url": f"/reset-password?token={reset_token}"
                })
        else:
            print(f"PASSWORD RESET: No user found for {email}")
        
        # Standard response (doesn't reveal if user exists)
        return JSONResponse(content={
            "success": True,
            "message": "If an account exists with this email, a password reset link has been sent."
        })
        
    except Exception as e:
        return JSONResponse(
            content={"error": f"Password reset request failed: {str(e)}"},
            status_code=500
        )

@app.post("/api/reset-password")
async def reset_password(request: Request):
    """Reset password with token"""
    if not auth_manager or not user_manager:
        return JSONResponse(
            content={"error": "Authentication not available"},
            status_code=500
        )
    
    try:
        data = await request.json()
        token = data.get("token")
        new_password = data.get("new_password")
        
        if not token or not new_password:
            return JSONResponse(
                content={"error": "Token and new password are required"},
                status_code=400
            )
        
        # Verify token and get email
        email = auth_manager.verify_password_reset_token(token)
        if not email:
            return JSONResponse(
                content={"error": "Invalid or expired reset token"},
                status_code=400
            )
        
        # Hash new password
        password_hash = auth_manager.hash_password(new_password)
        
        # Update password
        success = user_manager.update_password(email, password_hash)
        
        if not success:
            return JSONResponse(
                content={"error": "Failed to update password"},
                status_code=500
            )
        
        print(f"PASSWORD RESET SUCCESS: Password updated for {email}")
        
        # Send password changed notification
        if send_password_changed_email:
            try:
                # Get username for personalization
                user = user_manager.get_user_by_email(email)
                username = user.get("username", "there") if user else "there"
                
                email_result = send_password_changed_email(email, username)
                if email_result.get("success"):
                    print(f"✓ Password changed notification sent to {email}")
                else:
                    print(f"⚠ Password changed notification failed: {email_result.get('error')}")
            except Exception as e:
                print(f"⚠ Password changed notification error: {str(e)}")
        
        return JSONResponse(content={
            "success": True,
            "message": "Password has been reset successfully. You can now login with your new password."
        })
        
    except Exception as e:
        return JSONResponse(
            content={"error": f"Password reset failed: {str(e)}"},
            status_code=500
        )

@app.get("/api/pattern-descriptions")
async def get_pattern_descriptions():
    """Get all pattern descriptions"""
    descriptions = load_pattern_descriptions()
    return JSONResponse(content=descriptions)

@app.post("/api/pattern-descriptions")
async def update_pattern_description(request: Request):
    """Update a pattern description (admin only)"""
    # Check admin authentication
    admin = get_current_admin(request)
    if not admin:
        return JSONResponse(
            content={"error": "Admin authentication required"},
            status_code=401
        )
    
    try:
        data = await request.json()
        pattern_key = data.get("pattern_key")
        description = data.get("description")
        
        if not pattern_key:
            return JSONResponse(
                content={"error": "Pattern key is required"},
                status_code=400
            )
        
        descriptions = load_pattern_descriptions()
        
        if description:
            # Update or add description
            descriptions[pattern_key] = description
        else:
            # Remove description if empty
            descriptions.pop(pattern_key, None)
        
        save_pattern_descriptions(descriptions)
        
        return JSONResponse(content={
            "success": True,
            "message": "Description updated successfully"
        })
    except Exception as e:
        return JSONResponse(
            content={"error": str(e)},
            status_code=500
        )

@app.post("/api/fix-user-email/{user_id}")
async def fix_user_email(user_id: str, request: Request):
    """Fix user account that has email: null - creates account if doesn't exist"""
    if not user_manager:
        return JSONResponse(content={"error": "User manager not available"})
    
    try:
        data = await request.json()
        email = data.get("email")
        password = data.get("password")
        username = data.get("username", email.split('@')[0])  # Default username from email
        
        if not email or not password:
            return JSONResponse(
                content={"error": "Email and password required"},
                status_code=400
            )
        
        # Check if email is already used by another account
        existing_by_email = user_manager.get_user_by_email(email)
        if existing_by_email and existing_by_email.get("user_id") != user_id:
            return JSONResponse(
                content={"error": "Email already in use by another account. Please login instead."},
                status_code=400
            )
        
        # Get or create the user
        user = user_manager.get_user(user_id)
        
        # Hash the password
        password_hash = auth_manager.hash_password(password)
        
        if not user:
            # User doesn't exist - create a new one with this user_id
            print(f"CREATING NEW USER ACCOUNT: {user_id} with email: {email}")
            user = user_manager.create_user(user_id, email, password_hash, username)
        else:
            # User exists but missing email - update it
            print(f"FIXING EXISTING USER ACCOUNT: {user_id} with email: {email}")
            user["email"] = email
            user["password_hash"] = password_hash
            user["username"] = username
            user_manager.users[user_id] = user
            user_manager._save_users()
        
        # Create access token
        access_token = auth_manager.create_access_token(
            data={"sub": user_id, "email": email}
        )
        
        return JSONResponse(content={
            "success": True,
            "message": "Account saved successfully",
            "access_token": access_token,
            "user_id": user_id
        })
        
    except Exception as e:
        print(f"ERROR in fix_user_email: {str(e)}")
        return JSONResponse(
            content={"error": str(e)},
            status_code=500
        )

@app.get("/api/debug/user-count")
async def debug_user_count():
    """Debug endpoint to check registered users count"""
    if not user_manager:
        return JSONResponse(content={"error": "User manager not available"})
    
    total_users = len(user_manager.users)
    authenticated_users = sum(1 for u in user_manager.users.values() if u.get("email"))
    
    return JSONResponse(content={
        "total_users": total_users,
        "authenticated_users": authenticated_users,
        "user_ids": list(user_manager.users.keys())[:5]  # Show first 5 user IDs
    })


@app.get("/api/user-subscription-data")
async def get_user_subscription_data(request: Request):
    """Get detailed subscription data for the current user"""
    # Get current user
    current_user = await get_current_user_optional(request)
    if not current_user:
        return JSONResponse(
            content={"error": "Authentication required"},
            status_code=401
        )
    
    # Get user data
    user_data = None
    if user_manager:
        user_data = user_manager.get_user(current_user["user_id"])
    
    if not user_data:
        return JSONResponse(
            content={"error": "User not found"},
            status_code=404
        )
    
    return JSONResponse(content={
        "success": True,
        "user_data": user_data
    })

@app.post("/api/setup-password")
async def setup_password(request: Request):
    """Setup password for a user account"""
    if not auth_manager or not user_manager:
        return JSONResponse(
            content={"error": "Authentication not available"},
            status_code=500
        )
    
    try:
        # Get current user from token
        current_user = await get_current_user_optional(request)
        if not current_user:
            return JSONResponse(
                content={"error": "Authentication required"},
                status_code=401
            )
        
        data = await request.json()
        password = data.get("password")
        user_id = data.get("user_id")
        
        if not password:
            return JSONResponse(
                content={"error": "Password is required"},
                status_code=400
            )
        
        # Verify the user_id matches the authenticated user
        if user_id != current_user["user_id"]:
            return JSONResponse(
                content={"error": "Unauthorized"},
                status_code=403
            )
        
        # Hash password and update user
        password_hash = auth_manager.hash_password(password)
        user = user_manager.get_user(user_id)
        if user:
            user["password_hash"] = password_hash
            user_manager._save_users()
            
            return JSONResponse(content={
                "success": True,
                "message": "Password set successfully"
            })
        else:
            return JSONResponse(
                content={"error": "User not found"},
                status_code=404
            )
        
    except Exception as e:
        return JSONResponse(
            content={"error": f"Password setup failed: {str(e)}"},
            status_code=500
        )

@app.post("/api/create-checkout-session")
async def create_checkout_session(request: Request):
    """Create a Stripe checkout session for Pro subscription"""
    if not stripe_manager:
        return JSONResponse(
            content={"error": "Payment processing not available. Please check Stripe configuration."},
            status_code=500
        )
    
    # Check if Stripe environment variables are set
    stripe_secret = os.environ.get("STRIPE_SECRET_KEY")
    if not stripe_secret:
        return JSONResponse(
            content={"error": "Stripe configuration missing. Please set STRIPE_SECRET_KEY environment variable."},
            status_code=500
        )
    
    try:
        data = await request.json()
        user_id = data.get("user_id")
        email = data.get("email")
        password = data.get("password")  # Optional password for account creation
        
        if not email:
            return JSONResponse(
                content={"error": "Email is required"},
                status_code=400
            )
        
        # If no user_id provided, create a temporary one or find existing user
        if not user_id:
            if user_manager:
                # Check if user already exists by email
                existing_user = user_manager.get_user_by_email(email)
                if existing_user:
                    user_id = existing_user["user_id"]
                else:
                    # Create a temporary user ID for the payment flow
                    user_id = f"temp_{email.replace('@', '_').replace('.', '_')}_{int(datetime.now().timestamp())}"
            else:
                user_id = f"temp_{email.replace('@', '_').replace('.', '_')}_{int(datetime.now().timestamp())}"
        
        # Create success and cancel URLs
        base_url = str(request.base_url).rstrip('/')
        success_url = f"{base_url}/payment-success?session_id={{CHECKOUT_SESSION_ID}}&email={email}"
        cancel_url = f"{base_url}/pricing"
        
        # Create payment session
        result = create_payment_session(user_id, email, success_url, cancel_url)
        
        if result['success']:
            return JSONResponse(content={
                "success": True,
                "checkout_url": result['checkout_url'],
                "session_id": result['session_id'],
                "user_id": user_id
            })
        else:
            return JSONResponse(
                content={"error": f"Failed to create checkout session: {result['error']}"},
                status_code=500
            )
            
    except Exception as e:
        return JSONResponse(
            content={"error": f"Internal server error: {str(e)}"},
            status_code=500
        )

@app.get("/payment-success")
async def payment_success(request: Request, session_id: str = None, email: str = None):
    """Handle successful payment"""
    if not session_id:
        return templates.TemplateResponse("payment_error.html", {
            "request": request,
            "error": "No session ID provided"
        })
    
    try:
        import stripe
        session = stripe.checkout.Session.retrieve(session_id)
        
        if session.payment_status == 'paid':
            # Get user ID from session metadata
            user_id = session.metadata.get('user_id')
            subscription_id = session.subscription
            customer_email = session.customer_details.email if hasattr(session, 'customer_details') else email
            
            if user_id and subscription_id and user_manager:
                # Handle successful payment
                payment_result = handle_successful_payment(subscription_id, user_id)
                
                if payment_result['success']:
                    # Check if this is a temporary user (created during payment flow)
                    is_temp_user = user_id.startswith('temp_')
                    
                    if is_temp_user and customer_email:
                        # Convert temporary user to permanent user
                        # Check if user already exists by email
                        existing_user = user_manager.get_user_by_email(customer_email)
                        if existing_user:
                            # Update existing user with subscription
                            user_id = existing_user["user_id"]
                        else:
                            # Create new user with the email
                            user = user_manager.create_user(user_id, customer_email)
                    
                    # Update user subscription
                    try:
                        user_manager.update_stripe_subscription(
                            user_id,
                            payment_result['customer_id'],
                            subscription_id,
                            payment_result['status'],
                            payment_result.get('current_period_end')
                        )
                        
                        # Create access token for immediate login
                        access_token = None
                        if auth_manager and customer_email:
                            access_token = auth_manager.create_access_token(
                                data={"sub": user_id, "email": customer_email}
                            )
                        
                        return templates.TemplateResponse("payment_success.html", {
                            "request": request,
                            "user_id": user_id,
                            "subscription_id": subscription_id,
                            "email": customer_email,
                            "access_token": access_token,
                            "is_new_user": is_temp_user
                        })
                    except Exception as e:
                        print(f"Error updating user subscription: {e}")
                        return templates.TemplateResponse("payment_error.html", {
                            "request": request,
                            "error": f"Error updating subscription: {str(e)}"
                        })
                else:
                    return templates.TemplateResponse("payment_error.html", {
                        "request": request,
                        "error": f"Payment processing failed: {payment_result.get('error', 'Unknown error')}"
                    })
            else:
                return templates.TemplateResponse("payment_error.html", {
                    "request": request,
                    "error": "Missing user ID or subscription ID"
                })
        
        return templates.TemplateResponse("payment_error.html", {
            "request": request,
            "error": "Payment verification failed - payment not completed"
        })
        
    except Exception as e:
        print(f"Payment success error: {e}")
        return templates.TemplateResponse("payment_error.html", {
            "request": request,
            "error": f"Payment processing error: {str(e)}"
        })

@app.post("/api/create-portal-session")
async def create_portal_session(request: Request):
    """Create a Stripe customer portal session"""
    if not stripe_manager:
        return JSONResponse(
            content={"error": "Payment processing not available"},
            status_code=500
        )
    
    try:
        data = await request.json()
        user_id = data.get("user_id")
        
        if not user_id or not user_manager:
            return JSONResponse(
                content={"error": "User ID required"},
                status_code=400
            )
        
        user = user_manager.get_user(user_id)
        if not user or not user.get("stripe_customer_id"):
            return JSONResponse(
                content={"error": "No active subscription found"},
                status_code=404
            )
        
        # Create portal session
        base_url = str(request.base_url).rstrip('/')
        return_url = f"{base_url}/pricing"
        
        result = stripe_manager.create_customer_portal_session(
            user["stripe_customer_id"],
            return_url
        )
        
        if result['success']:
            return JSONResponse(content={
                "success": True,
                "portal_url": result['portal_url']
            })
        else:
            return JSONResponse(
                content={"error": result['error']},
                status_code=500
            )
            
    except Exception as e:
        return JSONResponse(
            content={"error": f"Failed to create portal session: {str(e)}"},
            status_code=500
        )

@app.post("/stripe-webhook")
async def stripe_webhook(request: Request):
    """Handle Stripe webhooks for subscription events"""
    if not stripe_manager:
        return JSONResponse(
            content={"error": "Payment processing not available"},
            status_code=500
        )
    
    try:
        payload = await request.body()
        signature = request.headers.get('stripe-signature')
        
        # Verify webhook signature
        if not stripe_manager.verify_webhook_signature(payload.decode('utf-8'), signature):
            return JSONResponse(
                content={"error": "Invalid webhook signature"},
                status_code=400
            )
        
        # Parse the event
        import stripe
        event = stripe.Webhook.construct_event(
            payload, signature, os.environ.get("STRIPE_WEBHOOK_SECRET")
        )
        
        # Handle different event types
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            user_id = session['metadata'].get('user_id')
            subscription_id = session['subscription']
            
            if user_id and subscription_id and user_manager:
                # Handle successful payment
                payment_result = handle_successful_payment(subscription_id, user_id)
                
                if payment_result['success']:
                    user_manager.update_stripe_subscription(
                        user_id,
                        payment_result['customer_id'],
                        subscription_id,
                        payment_result['status'],
                        payment_result.get('current_period_end')
                    )
        
        elif event['type'] == 'customer.subscription.updated':
            subscription = event['data']['object']
            user_id = subscription['metadata'].get('user_id')
            
            if user_id and user_manager:
                user_manager.update_stripe_subscription(
                    user_id,
                    subscription['customer'],
                    subscription['id'],
                    subscription['status'],
                    subscription.get('current_period_end')
                )
        
        elif event['type'] == 'customer.subscription.deleted':
            subscription = event['data']['object']
            user_id = subscription['metadata'].get('user_id')
            
            if user_id and user_manager:
                user_manager.cancel_stripe_subscription(user_id)
        
        return JSONResponse(content={"status": "success"})
        
    except Exception as e:
        print(f"Webhook error: {str(e)}")
        return JSONResponse(
            content={"error": f"Webhook processing failed: {str(e)}"},
            status_code=500
        )

@app.post("/api/upgrade/{user_id}")
async def upgrade_user(user_id: str, request: Request):
    """Create Stripe checkout session for user upgrade"""
    if not user_manager:
        return JSONResponse(
            content={"error": "User management not available"},
            status_code=500
        )
    
    try:
        # Get user data
        user_data = user_manager.get_user(user_id)
        if not user_data:
            return JSONResponse(
                content={"error": "User not found"},
                status_code=404
            )
        
        # Check if user already has a paid subscription
        if user_data.get("subscription") == "paid":
            return JSONResponse(
                content={"error": "User already has a paid subscription"},
                status_code=400
            )
        
        # Get user email (required for Stripe)
        email = user_data.get("email")
        if not email:
            return JSONResponse(
                content={"error": "Email required for upgrade. Please complete your account setup first."},
                status_code=400
            )
        
        # Track upgrade attempt
        user_manager.track_upgrade_attempt(user_id)
        
        # Create Stripe checkout session
        from stripe_integration import create_payment_session
        
        # Get current domain for success/cancel URLs
        base_url = str(request.base_url).rstrip('/')
        success_url = f"{base_url}/payment-success?user_id={user_id}"
        cancel_url = f"{base_url}/upload?user_id={user_id}&upgrade_cancelled=true"
        
        session_result = create_payment_session(user_id, email, success_url, cancel_url)
        
        if session_result.get('success'):
            return JSONResponse(content={
                "success": True,
                "checkout_url": session_result['checkout_url'],
                "session_id": session_result['session_id']
            })
        else:
            return JSONResponse(
                content={"error": f"Failed to create checkout session: {session_result.get('error', 'Unknown error')}"},
                status_code=500
            )
            
    except Exception as e:
        return JSONResponse(
            content={"error": f"Upgrade failed: {str(e)}"},
            status_code=500
        )

@app.post("/api/reset-usage/{user_id}")
async def reset_user_usage(user_id: str):
    """Reset user usage for testing purposes"""
    if user_manager:
        user_manager.reset_user_usage(user_id)
        return {"success": True, "message": "User usage reset successfully"}
    else:
        return {"error": "User management not available"}

@app.get("/api/debug/users")
async def debug_users():
    """Debug endpoint to see all users"""
    if user_manager:
        return {"users": user_manager.users}
    else:
        return {"error": "User management not available"}

@app.post("/api/debug/create-test-user")
async def create_test_user():
    """Create a fresh test user"""
    if user_manager:
        import uuid
        test_user_id = f"test_user_{uuid.uuid4().hex[:8]}"
        user_manager.create_user(test_user_id)
        return {"success": True, "user_id": test_user_id, "message": "Test user created"}
    else:
        return {"error": "User management not available"}

@app.post("/api/debug/delete-user/{user_id}")
async def delete_user(user_id: str):
    """Delete a user for testing purposes"""
    if user_manager:
        user_manager.delete_user(user_id)
        return {"success": True, "message": f"User {user_id} deleted"}
    else:
        return {"error": "User management not available"}

@app.get("/api/debug/clear-all-users")
async def clear_all_users():
    """Clear all user data for testing purposes - GET method for easy browser access"""
    if user_manager:
        user_manager.users = {}
        user_manager._save_users()
        print("🗑️ ALL USERS CLEARED - Fresh start")
        return JSONResponse(content={
            "success": True, 
            "message": "All users cleared successfully. You can now register with a fresh account.",
            "action": "Please clear your browser localStorage and register again"
        })
    else:
        return JSONResponse(content={"error": "User management not available"})


@app.post("/api/update-email/{user_id}")
async def update_user_email(user_id: str, request: Request):
    """Update user email address"""
    if not user_manager:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": "User management not available"}
        )
    
    try:
        data = await request.json()
        email = data.get("email")
        consent = data.get("consent", False)
        
        if not email:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "Email is required"}
            )
        
        # Update user with email
        user = user_manager.get_user(user_id)
        if not user:
            user_manager.create_user(user_id, email)
        else:
            user["email"] = email
            user["email_consent"] = consent
            user_manager._save_users()
        
        return {"success": True, "message": "Email updated successfully"}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )


@app.post("/analyze")
async def analyze(file: UploadFile = File(...), user_id: str = Form("user_id")):
    print(f"DEBUG: Analyze called with user_id: {user_id}, file: {file.filename}")
    
    try:
        # Check user authentication and usage limits BEFORE processing
        user = None
        is_authenticated = False
        usage_status = None
    
    if user_manager:
        user = user_manager.get_user(user_id)
        print(f"DEBUG: User found: {user is not None}")
        
        # CRITICAL: Only check usage limits for users with email addresses (authenticated users)
        # Visitors (users without email) should have unlimited uploads but must register to see results
        if user and user.get("email"):
            # Authenticated user - check usage limits
            is_authenticated = True
            usage_status = user_manager.get_usage_summary(user_id)
            print(f"DEBUG: Authenticated user - usage: {usage_status}")
            
            # Check if user can upload (within limits)
            if not user_manager.can_upload_document(user_id):
                return JSONResponse(
                    content={
                        "success": False,
                        "error": "Monthly limit reached",
                        "upgrade_required": True,
                        "usage": usage_status,
                        "message": f"You've used {usage_status.get('documents_this_month', 0)}/{usage_status.get('monthly_limit', 3)} documents this month. Upgrade to continue analyzing documents."
                    }, 
                    status_code=429
                )
        else:
            # Visitor user (no email) - check daily fair use limits
            # This includes both: users who don't exist in DB AND users who exist but have no email
            print(f"DEBUG: Visitor user - checking daily limits (user_exists={user is not None}, has_email={user.get('email') if user else None})")
            
            # Check visitor daily limits (fair use policy)
            # Allow 2 uploads, then prompt for account creation on 3rd attempt
            visitor_uploads_today = get_visitor_uploads_today(request)
            
            if visitor_uploads_today >= 2:
                return JSONResponse(
                    content={
                        "success": False,
                        "error": "Account required",
                        "requires_account": True,
                        "message": "Create an account or sign in to analyze this document"
                    }, 
                    status_code=401
                )
            
            usage_status = {
                "subscription": "visitor",
                "email": None,
                "documents_this_month": 0,
                "total_documents": 0,
                "monthly_limit": 3,
                "can_upload": True,
                "visitor_uploads_today": visitor_uploads_today,
                "visitor_daily_limit": 2
            }
    
    # Validate file upload
    from error_handler import validate_file_upload, handle_upload_error, create_user_friendly_response
    
    validation_result = validate_file_upload(file)
    if not validation_result.get("valid", False):
        return JSONResponse(
            content=create_user_friendly_response(validation_result),
            status_code=400
        )
    
    file_info = validation_result["file_info"]
    file_type = file_info["type"]
    
    # Save file temporarily with correct extension
    import tempfile
    import os
    
    # Create a temporary file with proper extension
    temp_fd, temp_path = tempfile.mkstemp(suffix=f'.{file_type}')
    os.close(temp_fd)
    
    with open(temp_path, "wb") as f:
        f.write(await file.read())

    try:
        # Load patterns
        patterns = load_custom_patterns()
        pending = load_pending_patterns()

        # Extract text using the appropriate processor for the file type
        from file_processor import extract_text_from_file
        
        file_extraction = extract_text_from_file(temp_path, file_type)
        raw_pages = file_extraction["pages"]
        quality_assessment = file_extraction["quality_assessment"]
        total_characters = file_extraction["total_characters"]
        readable_pages = file_extraction["readable_pages"]
        total_pages = file_extraction["total_pages"]
        quality_issues = file_extraction["quality_issues"]
        
        # Handle different quality scenarios
        if quality_assessment == "unreadable":
            # Revert usage since this doesn't count as a successful upload
            if user_manager:
                user_manager.revert_usage(user_id)
            return JSONResponse(
                content={
                    "error": "PDF is unreadable",
                    "details": "The uploaded PDF appears to be a scanned image without text. Please upload a better quality scan or a PDF with selectable text.",
                    "quality_issues": quality_issues,
                    "quality_assessment": quality_assessment,
                    "readable_pages": readable_pages,
                    "total_pages": total_pages
                }, 
                status_code=400
            )
        
        elif quality_assessment in ["poor", "fair"]:
            # Revert usage since this doesn't count as a successful upload
            if user_manager:
                user_manager.revert_usage(user_id)
            return JSONResponse(
                content={
                    "error": "Poor quality scan detected",
                    "details": f"The tool was able to read {readable_pages} out of {total_pages} pages, but the quality is insufficient for a complete analysis. This may miss important risks and benefits. Please upload a higher quality scan.",
                    "quality_issues": quality_issues,
                    "quality_assessment": quality_assessment,
                    "readable_pages": readable_pages,
                    "total_pages": total_pages,
                    "total_characters": total_characters
                }, 
                status_code=400
            )
        
        elif not raw_pages:
            # Revert usage since this doesn't count as a successful upload
            if user_manager:
                user_manager.revert_usage(user_id)
            return JSONResponse(
                content={
                    "error": "Unable to extract text from PDF",
                    "details": "The PDF could not be processed. Please ensure it's not corrupted and contains readable text."
                }, 
                status_code=400
            )
        
        # Run analysis on the already extracted text
        full_text = " ".join([p["text"] for p in raw_pages if p["text"]])
        
        # Use the analyzer with the extracted text instead of re-processing the file
        from analyzer import analyze_text_content
        analysis_result = analyze_text_content(full_text)

        # Add new patterns to pending
        for category in ["risks", "good_points"]:
            # Flatten results — might be dict of categories or list of phrases
            matches = []
            if isinstance(analysis_result.get(category), dict):
                for subcat_phrases in analysis_result[category].values():
                    matches.extend(subcat_phrases)
            elif isinstance(analysis_result.get(category), list):
                matches = analysis_result[category]

            for phrase in matches:
                # Normalize phrase to string
                if isinstance(phrase, dict):
                    phrase_text = phrase.get('match') or phrase.get('phrase') or str(phrase)
                else:
                    phrase_text = str(phrase)
                
                # Check for exact duplicates (not substring matches)
                already_custom = any(
                    phrase_text == str(existing_phrase)
                    for phrases in patterns.get(category, {}).values()
                    for existing_phrase in phrases
                )
                already_pending = any(
                    phrase_text == str(existing_phrase)
                    for phrases in pending.get(category, {}).values()
                    for existing_phrase in phrases
                )
                if not already_custom and not already_pending:
                    pending.setdefault(category, {}).setdefault("general", []).append(phrase_text)

        save_pending_patterns(pending)

        if is_authenticated:
            # Record usage for authenticated users
            if user_manager:
                print(f"📊 Recording document upload for user: {user_id}")
                success = user_manager.record_document_upload(user_id)
                print(f"📊 Usage recording result: {success}")
            
            # Authenticated user response - full analysis
            response_data = {
                "success": True,
                "filename": file.filename,
                "analysis": analysis_result,
                "pages": raw_pages,  # send raw text for highlighting
                "custom_patterns": patterns,
                "pending_patterns": pending,
                "quality_assessment": quality_assessment,
                "readable_pages": readable_pages,
                "total_pages": total_pages,
                "total_characters": total_characters,
                "quality_issues": quality_issues,
                "usage": usage_status  # Include updated usage info
            }
            print(f"DEBUG: Returning full analysis for authenticated user")
        else:
            # Record visitor upload for fair use tracking
            record_visitor_upload(request)
            
            # Visitor response - store analysis but don't show any details
            response_data = {
                "success": True,
                "filename": file.filename,
                "requires_auth": True,
                "message": "Please create an account or log in to see your analysis results.",
                "analysis": analysis_result,  # Include full analysis for post-auth display (hidden from visitor)
                "quality_assessment": quality_assessment,
                "readable_pages": readable_pages,
                "total_pages": total_pages,
                "total_characters": total_characters,
                "usage": usage_status  # Include usage info for visitor
            }
            print(f"DEBUG: Returning visitor response with hidden analysis")
        
        return JSONResponse(content=response_data)
    
    except Exception as e:
        # Handle processing errors with user-friendly messages
        from error_handler import handle_processing_error, create_user_friendly_response, log_error
        
        print(f"DEBUG: Exception in analyze function: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Log the error for debugging
        log_error(e, {"user_id": user_id, "file_type": file_type, "file_info": file_info})
        
        # Create user-friendly error response
        error_response = handle_processing_error(e, file_info)
        user_response = create_user_friendly_response(error_response)
        
        return JSONResponse(
            content=user_response,
            status_code=500
        )
    
    finally:
        # Clean up temporary file
        try:
            os.unlink(temp_path)
        except:
            pass
    
    except Exception as e:
        print(f"CRITICAL ERROR in analyze endpoint: {e}")
        import traceback
        traceback.print_exc()
        
        return JSONResponse(
            content={
                "success": False,
                "error": "Internal server error",
                "message": "An unexpected error occurred. Please try again."
            },
            status_code=500
        )


@app.post("/analyze-text")
async def analyze_text(request: Request):
    """Analyze pasted text instead of uploaded file"""
    try:
        data = await request.json()
        text_content = data.get("text", "").strip()
        user_id = data.get("user_id", "")
        
        if not text_content:
            return JSONResponse(
                content={"error": "No text provided"}, 
                status_code=400
            )
        
        # Check if user is authenticated (has email)
        user = None
        is_authenticated = False
        
        if user_manager:
            user = user_manager.get_user(user_id)
            if user and user.get("email"):
                is_authenticated = True
                # Check usage limits for authenticated users
                if not user_manager.can_upload_document(user_id):
                    return JSONResponse(
                        content={
                            "error": "Monthly limit reached", 
                            "upgrade_required": True,
                            "usage": user_manager.get_usage_summary(user_id)
                        }, 
                        status_code=429
                    )
        
        if not is_authenticated:
            # Check visitor daily limits for text analysis too
            # Allow 2 uploads, then prompt for account creation on 3rd attempt
            visitor_uploads_today = get_visitor_uploads_today(request)
            
            if visitor_uploads_today >= 2:
                return JSONResponse(
                    content={
                        "success": False,
                        "error": "Account required",
                        "requires_account": True,
                        "message": "Create an account or sign in to analyze this document"
                    }, 
                    status_code=401
                )
        
        # Load patterns
        patterns = load_custom_patterns()
        pending = load_pending_patterns()

        # Run analysis on the provided text
        analysis_result = analyze_text_content(text_content)

        # Add new patterns to pending (already handled by detect_new_patterns function)
        # The detect_new_patterns function automatically saves new patterns to pending_patterns.json
        
        save_pending_patterns(pending)

        if is_authenticated:
            # Record usage for authenticated users
            if user_manager:
                user_manager.record_document_upload(user_id)
            
            # Authenticated user response - full analysis
            response_data = {
                "success": True,
                "filename": "Text Input",
                "analysis": analysis_result,
                "analysis_type": "text"
            }
        else:
            # Record visitor upload for fair use tracking
            record_visitor_upload(request)
            
            # Visitor response - requires authentication
            response_data = {
                "success": True,
                "filename": "Text Input",
                "requires_auth": True,
                "message": "Please create an account or log in to see your analysis results.",
                "analysis": analysis_result,  # Include full analysis for post-auth display (hidden from visitor)
                "analysis_type": "text"
            }
        
        print(f"DEBUG: Returning analysis for authenticated user")
        
        return JSONResponse(content=response_data)
        
    except Exception as e:
        print(f"Error in analyze_text: {str(e)}")
        return JSONResponse(
            content={"error": f"Analysis failed: {str(e)}"}, 
            status_code=500
        )


@app.post("/add_pattern")
async def add_pattern(data: dict):
    """Add a new pattern to pending patterns"""
    category = data.get("category", "general")
    phrase = data.get("phrase", "")
    pattern_type = data.get("type", "risk")  # "risk" or "good_point"
    
    if not phrase:
        return JSONResponse(content={"error": "No phrase provided"}, status_code=400)
    
    pending = load_pending_patterns()
    patterns = load_custom_patterns()
    
    # Convert type to the correct key
    type_key = "risks" if pattern_type == "risk" else "good_points"
    
    # Check for duplicates
    already_custom = any(
        phrase == str(existing_phrase)
        for phrases in patterns.get(type_key, {}).values()
        for existing_phrase in phrases
    )
    already_pending = any(
        phrase == str(existing_phrase)
        for phrases in pending.get(type_key, {}).values()
        for existing_phrase in phrases
    )
    
    if already_custom:
        return JSONResponse(content={"error": "Pattern already exists in custom patterns"}, status_code=400)
    elif already_pending:
        return JSONResponse(content={"error": "Pattern already exists in pending patterns"}, status_code=400)
    
    # Add to pending patterns
    pending.setdefault(type_key, {}).setdefault(category, []).append(phrase)
    
    save_pending_patterns(pending)
    
    return JSONResponse(content={"message": "Pattern added to pending"})



@app.get("/cleanup_duplicates")
async def cleanup_duplicates():
    """Clean up duplicate patterns in both custom and pending pattern files"""
    patterns = load_custom_patterns()
    pending = load_pending_patterns()
    
    cleaned_custom = {"risks": {}, "good_points": {}}
    cleaned_pending = {"risks": {}, "good_points": {}}
    
    # Clean custom patterns
    for category in ["risks", "good_points"]:
        for subcategory, phrases in patterns.get(category, {}).items():
            unique_phrases = list(dict.fromkeys(phrases))  # Remove duplicates while preserving order
            if unique_phrases:
                cleaned_custom[category][subcategory] = unique_phrases
    
    # Clean pending patterns
    for category in ["risks", "good_points"]:
        for subcategory, phrases in pending.get(category, {}).items():
            unique_phrases = list(dict.fromkeys(phrases))  # Remove duplicates while preserving order
            if unique_phrases:
                cleaned_pending[category][subcategory] = unique_phrases
    
    # Save cleaned patterns
    save_custom_patterns(cleaned_custom)
    save_pending_patterns(cleaned_pending)
    
    return JSONResponse(content={
        "message": "Duplicates cleaned up successfully",
        "custom_patterns": cleaned_custom,
        "pending_patterns": cleaned_pending
    })


@app.get("/search_patterns")
async def search_patterns(query: str = ""):
    """Search for patterns in both custom and pending patterns"""
    patterns = load_custom_patterns()
    pending = load_pending_patterns()
    
    results = {
        "custom_patterns": [],
        "pending_patterns": [],
        "total_custom": 0,
        "total_pending": 0
    }
    
    # Search in custom patterns
    for category, subcategories in patterns.items():
        for subcategory, phrases in subcategories.items():
            for phrase in phrases:
                if query.lower() in phrase.lower():
                    results["custom_patterns"].append({
                        "category": category,
                        "subcategory": subcategory,
                        "phrase": phrase
                    })
                results["total_custom"] += 1
    
    # Search in pending patterns
    for category, subcategories in pending.items():
        for subcategory, phrases in subcategories.items():
            for phrase in phrases:
                if query.lower() in phrase.lower():
                    results["pending_patterns"].append({
                        "category": category,
                        "subcategory": subcategory,
                        "phrase": phrase
                    })
                results["total_pending"] += 1
    
    return JSONResponse(content=results)


@app.get("/pending_patterns")
async def get_pending_patterns():
    pending = load_pending_patterns()
    
    # Convert to the format expected by the frontend
    formatted_patterns = []
    
    for category, subcategories in pending.items():
        for subcategory, data in subcategories.items():
            if isinstance(data, dict) and "patterns" in data:
                # New format with scores
                score = data.get("score", 3)
                for phrase in data["patterns"]:
                    formatted_patterns.append({
                        "type": "risk" if category == "risks" else "good_point",
                        "category": subcategory,
                        "phrase": phrase,
                        "score": score,
                        "scored": True
                    })
            else:
                # Legacy format (list of phrases)
                for phrase in data:
                    formatted_patterns.append({
                        "type": "risk" if category == "risks" else "good_point",
                        "category": subcategory,
                        "phrase": phrase,
                        "scored": False
                    })
    
    return JSONResponse(content=formatted_patterns)


@app.get("/existing_categories")
async def get_existing_categories():
    """Get all existing categories from core patterns and custom patterns (active patterns only)"""
    custom_patterns = load_custom_patterns()
    
    # Get categories from custom patterns (active patterns)
    custom_categories = {
        "risks": list(custom_patterns.get("risks", {}).keys()),
        "good_points": list(custom_patterns.get("good_points", {}).keys())
    }
    
    # Get categories from core patterns (established patterns)
    core_categories = {
        "risks": list(RISK_PATTERNS.keys()),
        "good_points": list(GOOD_PATTERNS.keys())
    }
    
    # Combine and deduplicate - only from active/established patterns
    all_categories = {
        "risks": sorted(list(set(custom_categories["risks"] + core_categories["risks"]))),
        "good_points": sorted(list(set(custom_categories["good_points"] + core_categories["good_points"])))
    }
    
    return JSONResponse(content=all_categories)





@app.post("/score_pattern")
async def score_pattern(data: dict):
    phrase = data.get("phrase")
    pattern_type = data.get("type")
    category = data.get("category")
    score = data.get("score", 3)
    
    if pattern_type not in ["risk", "good_point"]:
        return JSONResponse(content={"error": "Invalid pattern type"}, status_code=400)
    
    if not category:
        return JSONResponse(content={"error": "Category is required"}, status_code=400)
    
    if not isinstance(score, int) or score < 1 or score > 5:
        return JSONResponse(content={"error": "Score must be between 1 and 5"}, status_code=400)
    
    # Convert frontend type to backend category
    backend_category = "risks" if pattern_type == "risk" else "good_points"
    
    pending = load_pending_patterns()
    custom_patterns = load_custom_patterns()
    
    # Remove the pattern from pending patterns
    for cat_key, subcategories in pending.items():
        for subcat_key, subcat_data in list(subcategories.items()):
            if isinstance(subcat_data, dict) and "patterns" in subcat_data:
                # New format
                if phrase in subcat_data["patterns"]:
                    subcat_data["patterns"].remove(phrase)
                    if not subcat_data["patterns"]:
                        del subcategories[subcat_key]
            elif isinstance(subcat_data, list):
                # Legacy format
                if phrase in subcat_data:
                    subcat_data.remove(phrase)
                    if not subcat_data:
                        del subcategories[subcat_key]
    
    # Add the pattern to custom_patterns.json (active patterns used for detection)
    if backend_category not in custom_patterns:
        custom_patterns[backend_category] = {}
    
    if category not in custom_patterns[backend_category]:
        custom_patterns[backend_category][category] = []
    
    # Add the pattern if it's not already there
    if phrase not in custom_patterns[backend_category][category]:
        custom_patterns[backend_category][category].append(phrase)
    
    # Save both files
    save_pending_patterns(pending)
    save_custom_patterns(custom_patterns)
    
    return JSONResponse(content={"message": "Pattern scored and moved to active patterns"})


@app.post("/reject_pattern")
async def reject_pattern(data: dict):
    phrase = data.get("phrase")

    pending = load_pending_patterns()
    
    # Remove the pattern from any location
    for cat_key, subcategories in pending.items():
        for subcat_key, subcat_data in list(subcategories.items()):
            if isinstance(subcat_data, dict) and "patterns" in subcat_data:
                # New format
                if phrase in subcat_data["patterns"]:
                    subcat_data["patterns"].remove(phrase)
                    if not subcat_data["patterns"]:
                        del subcategories[subcat_key]
            elif isinstance(subcat_data, list):
                # Legacy format
                if phrase in subcat_data:
                    subcat_data.remove(phrase)
                    if not subcat_data:
                        del subcategories[subcat_key]

    save_pending_patterns(pending)
    return JSONResponse(content={"message": "Pattern rejected"})


@app.post("/compare")
async def compare_documents(file1: UploadFile = File(...), file2: UploadFile = File(...), user_id: str = Form("user_id")):
    """Compare two documents side-by-side (paid users only)"""
    
    if not user_manager:
        return JSONResponse(
            content={"error": "User management not available"},
            status_code=500
        )
    
    # Check if user is paid
    user = user_manager.get_user(user_id)
    if not user or user["subscription"] != "paid":
        return JSONResponse(
            content={"error": "Side-by-side comparison is a Pro feature. Please upgrade to use this feature."},
            status_code=403
        )
    
    # Save files temporarily
    import tempfile
    import os
    
    temp_fd1, temp_path1 = tempfile.mkstemp(suffix='.pdf')
    temp_fd2, temp_path2 = tempfile.mkstemp(suffix='.pdf')
    os.close(temp_fd1)
    os.close(temp_fd2)
    
    try:
        # Save uploaded files
        with open(temp_path1, "wb") as f:
            f.write(await file1.read())
        with open(temp_path2, "wb") as f:
            f.write(await file2.read())
        
        # Analyze both documents
        analysis1 = analyze_pdf(temp_path1)
        analysis2 = analyze_pdf(temp_path2)
        
        # Calculate risk scores
        risk_score1 = calculate_risk_score(analysis1)
        risk_score2 = calculate_risk_score(analysis2)
        
        # Count findings
        risks_count1 = sum(len(items) for items in analysis1.get("risks", {}).values())
        good_points_count1 = sum(len(items) for items in analysis1.get("good_points", {}).values())
        risks_count2 = sum(len(items) for items in analysis2.get("risks", {}).values())
        good_points_count2 = sum(len(items) for items in analysis2.get("good_points", {}).values())
        
        # Find differences
        differences = find_document_differences(analysis1, analysis2)
        
        comparison_data = {
            "doc1": {
                "risk_score": risk_score1,
                "risks_count": risks_count1,
                "good_points_count": good_points_count1,
                "risks": analysis1.get("risks", {}),
                "good_points": analysis1.get("good_points", {})
            },
            "doc2": {
                "risk_score": risk_score2,
                "risks_count": risks_count2,
                "good_points_count": good_points_count2,
                "risks": analysis2.get("risks", {}),
                "good_points": analysis2.get("good_points", {})
            },
            "differences": differences
        }
        
        return JSONResponse(content=comparison_data)
        
    finally:
        # Clean up temporary files
        try:
            os.unlink(temp_path1)
            os.unlink(temp_path2)
        except:
            pass


def calculate_risk_score(analysis):
    """Calculate a risk score from 1-10 based on analysis results"""
    risks = analysis.get("risks", {})
    good_points = analysis.get("good_points", {})
    
    # Count total findings
    total_risks = sum(len(items) for items in risks.values())
    total_good_points = sum(len(items) for items in good_points.values())
    
    # Simple scoring algorithm
    if total_risks == 0 and total_good_points == 0:
        return 5  # Neutral
    
    # Base score starts at 5, adjust based on risk/good point ratio
    score = 5
    
    if total_risks > 0:
        # Deduct points for risks (more risks = lower score)
        risk_penalty = min(total_risks * 0.5, 4)  # Max 4 point penalty
        score -= risk_penalty
    
    if total_good_points > 0:
        # Add points for good points (more good points = higher score)
        good_bonus = min(total_good_points * 0.3, 3)  # Max 3 point bonus
        score += good_bonus
    
    return max(1, min(10, round(score)))


def find_document_differences(analysis1, analysis2):
    """Find key differences between two document analyses"""
    differences = []
    
    # Compare risk counts
    risks1 = sum(len(items) for items in analysis1.get("risks", {}).values())
    risks2 = sum(len(items) for items in analysis2.get("risks", {}).values())
    
    if risks1 != risks2:
        diff = abs(risks1 - risks2)
        if risks1 > risks2:
            differences.append({
                "type": "Risk Level",
                "description": f"Document 1 has {diff} more risk(s) than Document 2"
            })
        else:
            differences.append({
                "type": "Risk Level", 
                "description": f"Document 2 has {diff} more risk(s) than Document 1"
            })
    
    # Compare good point counts
    good_points1 = sum(len(items) for items in analysis1.get("good_points", {}).values())
    good_points2 = sum(len(items) for items in analysis2.get("good_points", {}).values())
    
    if good_points1 != good_points2:
        diff = abs(good_points1 - good_points2)
        if good_points1 > good_points2:
            differences.append({
                "type": "Favorable Terms",
                "description": f"Document 1 has {diff} more favorable term(s) than Document 2"
            })
        else:
            differences.append({
                "type": "Favorable Terms",
                "description": f"Document 2 has {diff} more favorable term(s) than Document 1"
            })
    
    # Compare specific categories
    categories1 = set(analysis1.get("risks", {}).keys()) | set(analysis1.get("good_points", {}).keys())
    categories2 = set(analysis2.get("risks", {}).keys()) | set(analysis2.get("good_points", {}).keys())
    
    unique_to_1 = categories1 - categories2
    unique_to_2 = categories2 - categories1
    
    if unique_to_1:
        differences.append({
            "type": "Unique Categories",
            "description": f"Document 1 has unique categories: {', '.join(unique_to_1)}"
        })
    
    if unique_to_2:
        differences.append({
            "type": "Unique Categories",
            "description": f"Document 2 has unique categories: {', '.join(unique_to_2)}"
        })
    
    return differences


if __name__ == "__main__":
    import uvicorn
    import os
    
    # Get port from environment variable, default to 8000
    port = int(os.environ.get("PORT", 8000))
    
    uvicorn.run(app, host="0.0.0.0", port=port, reload=True)