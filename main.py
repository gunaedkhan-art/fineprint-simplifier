# Minimal FastAPI app for testing deployment
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import json
from datetime import datetime

# Test custom module imports
try:
    from core_patterns import RISK_PATTERNS, GOOD_PATTERNS
    print("✓ core_patterns imported successfully")
except Exception as e:
    print(f"✗ core_patterns import failed: {e}")
    RISK_PATTERNS = {}
    GOOD_PATTERNS = {}

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
    from user_management import user_manager
    print("✓ user_management imported successfully")
except Exception as e:
    print(f"✗ user_management import failed: {e}")
    user_manager = None

try:
    from matcher import find_risks_in_text
    print("✓ matcher imported successfully")
except Exception as e:
    print(f"✗ matcher import failed: {e}")
    find_risks_in_text = None

try:
    from pdf_parser import extract_text_from_pdf
    print("✓ pdf_parser imported successfully")
except Exception as e:
    print(f"✗ pdf_parser import failed: {e}")
    extract_text_from_pdf = None

try:
    from analyzer import analyze_pdf
    print("✓ analyzer imported successfully")
except Exception as e:
    print(f"✗ analyzer import failed: {e}")
    analyze_pdf = None

try:
    from admin import router as admin_router
    print("✓ admin router imported successfully")
except Exception as e:
    print(f"✗ admin router import failed: {e}")
    admin_router = None

app = FastAPI()

# Serve static files (CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up Jinja2 templating
templates = Jinja2Templates(directory="templates")

# Include admin router if available
if admin_router:
    try:
        app.include_router(admin_router)
        print("✓ admin router included successfully")
    except Exception as e:
        print(f"✗ admin router inclusion failed: {e}")

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "app": "Fineprint Simplifier"
    }

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/test")
async def test():
    return {
        "message": "Fineprint Simplifier is running with all modules including admin router!",
        "risk_patterns_count": len(RISK_PATTERNS),
        "good_patterns_count": len(GOOD_PATTERNS),
        "pricing_loaded": bool(PRICING),
        "user_manager_loaded": user_manager is not None,
        "matcher_loaded": find_risks_in_text is not None,
        "pdf_parser_loaded": extract_text_from_pdf is not None,
        "analyzer_loaded": analyze_pdf is not None,
        "admin_router_loaded": admin_router is not None
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
