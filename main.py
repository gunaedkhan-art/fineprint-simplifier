# fineprint_simplifier/main.py

from fastapi import FastAPI, UploadFile, File, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from collections import defaultdict
from pdf_parser import extract_text_from_pdf
from preprocess_text import preprocess_text
from matcher import find_risks_in_text
from analyzer import analyze_pdf, analyze_text_content
import os
import json
import re
from datetime import datetime

# Test custom module imports with error handling
try:
    from core_patterns import RISK_PATTERNS, GOOD_PATTERNS  # live update support
    print("✓ core_patterns imported successfully")
except Exception as e:
    print(f"✗ core_patterns import failed: {e}")
    RISK_PATTERNS = {}
    GOOD_PATTERNS = {}

try:
    from user_management import user_manager
    print("✓ user_management imported successfully")
except Exception as e:
    print(f"✗ user_management import failed: {e}")
    user_manager = None

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

app = FastAPI()

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app):
    """Handle startup and shutdown events"""
    print("🚀 Application starting up...")
    try:
        print("✓ FastAPI app created successfully")
    except Exception as e:
        print(f"✗ Startup error: {e}")
    yield
    print("🛑 Application shutting down...")

app = FastAPI(lifespan=lifespan)

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


# -------------------------
# Routes
# -------------------------
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/upload", response_class=HTMLResponse)
async def upload_page(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})

@app.get("/compare", response_class=HTMLResponse)
async def compare_page(request: Request):
    return templates.TemplateResponse("compare.html", {"request": request})

@app.get("/how-it-works", response_class=HTMLResponse)
async def how_it_works_page(request: Request):
    return templates.TemplateResponse("how-it-works.html", {"request": request})


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    # Absolute minimal health check with no external dependencies
    return {"status": "healthy"}

@app.get("/ping")
async def ping():
    """Simple ping endpoint for testing"""
    return {"message": "pong"}

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Fineprint Simplifier is running!"}

# Include admin router if available
if admin_router:
    try:
        app.include_router(admin_router)
        print("✓ admin router included successfully")
    except Exception as e:
        print(f"✗ admin router inclusion failed: {e}")
else:
    print("⚠ admin router not available")

@app.get("/pricing", response_class=HTMLResponse)
async def pricing_page(request: Request):
    return templates.TemplateResponse("pricing.html", {"request": request})


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
        
        # If user doesn't exist or has no email, they're a visitor
        if not user or not user.get("email"):
            # Visitors can always upload (no limits)
            return {
                "subscription": "free",
                "email": None,
                "documents_this_month": 0,
                "total_documents": 0,
                "monthly_limit": 3,
                "can_upload": True  # Visitors can always upload
            }
        
        # For logged-in users, get normal usage summary
        return user_manager.get_usage_summary(user_id)
    else:
        return {"error": "User management not available"}


@app.post("/api/upgrade/{user_id}")
async def upgrade_user(user_id: str):
    """Upgrade user to paid tier (placeholder for payment integration)"""
    if user_manager:
        user_manager.upgrade_user(user_id, "paid")
        return {"success": True, "message": "User upgraded to paid tier"}
    else:
        return {"error": "User management not available"}

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

@app.post("/api/debug/clear-all-users")
async def clear_all_users():
    """Clear all user data for testing purposes"""
    if user_manager:
        user_manager.users = {}
        user_manager._save_users()
        return {"success": True, "message": "All users cleared"}
    else:
        return {"error": "User management not available"}


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
    # For visitors, we don't check any existing user data - just allow the upload
    # and create a fresh user record after successful analysis
    is_visitor = True
    user = None
    
    # Only check existing user data if they have an email (logged in user)
    if user_manager:
        user = user_manager.get_user(user_id)
        if user and user.get("email"):
            is_visitor = False
            # Check usage limits for logged in users only
            if not user_manager.update_usage(user_id):
                return JSONResponse(
                    content={
                        "error": "Monthly limit reached", 
                        "upgrade_required": True,
                        "usage": user_manager.get_usage_summary(user_id)
                    }, 
                    status_code=429
                )
    
    # Save file temporarily
    import tempfile
    import os
    
    # Create a temporary file with proper extension
    temp_fd, temp_path = tempfile.mkstemp(suffix='.pdf')
    os.close(temp_fd)
    
    with open(temp_path, "wb") as f:
        f.write(await file.read())

    try:
        # Load patterns
        patterns = load_custom_patterns()
        pending = load_pending_patterns()

        # Extract text (page-by-page) with quality assessment
        pdf_extraction = extract_text_from_pdf(temp_path)
        raw_pages = pdf_extraction["pages"]
        quality_assessment = pdf_extraction["quality_assessment"]
        total_characters = pdf_extraction["total_characters"]
        readable_pages = pdf_extraction["readable_pages"]
        total_pages = pdf_extraction["total_pages"]
        quality_issues = pdf_extraction["quality_issues"]
        
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
        
        # Run analysis on the entire document text
        full_text = " ".join([p["text"] for p in raw_pages if p["text"]])
        analysis_result = analyze_pdf(temp_path)  # Should return dict with 'risks' and 'good_points'

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

        # Count findings for visitor summary
        risk_count = 0
        good_point_count = 0
        
        if isinstance(analysis_result.get("risks"), dict):
            for category_risks in analysis_result["risks"].values():
                risk_count += len(category_risks)
        elif isinstance(analysis_result.get("risks"), list):
            risk_count = len(analysis_result["risks"])
            
        if isinstance(analysis_result.get("good_points"), dict):
            for category_good_points in analysis_result["good_points"].values():
                good_point_count += len(category_good_points)
        elif isinstance(analysis_result.get("good_points"), list):
            good_point_count = len(analysis_result["good_points"])

        if is_visitor:
            # For visitors, create a fresh user record after successful analysis
            if user_manager:
                user_manager.create_user(user_id)  # This creates a clean visitor record
                user_manager.update_usage(user_id)  # Update usage for the new record
            
            # Visitor response - only show summary
            response_data = {
                "is_visitor": True,
                "visitor_summary": {
                    "risk_count": risk_count,
                    "good_point_count": good_point_count,
                    "total_pages": total_pages,
                    "quality_assessment": quality_assessment
                },
                "message": "Analysis complete! Sign up to see detailed results."
            }
        else:
            # Logged in user response - full analysis
            response_data = {
                "is_visitor": False,
                "analysis": analysis_result,
                "pages": raw_pages,  # send raw text for highlighting
                "custom_patterns": patterns,
                "pending_patterns": pending,
                "quality_assessment": quality_assessment,
                "readable_pages": readable_pages,
                "total_pages": total_pages,
                "total_characters": total_characters,
                "quality_issues": quality_issues
            }
        
        print(f"DEBUG: Returning response for {'visitor' if is_visitor else 'logged in user'}")
        print(f"DEBUG: Risk count: {risk_count}, Good point count: {good_point_count}")
        
        return JSONResponse(content=response_data)
    finally:
        # Clean up temporary file
        try:
            os.unlink(temp_path)
        except:
            pass


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
        
        # For visitors, we don't check any existing user data - just allow the analysis
        # and create a fresh user record after successful analysis
        is_visitor = True
        user = None
        
        # Only check existing user data if they have an email (logged in user)
        if user_manager:
            user = user_manager.get_user(user_id)
            if user and user.get("email"):
                is_visitor = False
                # Check usage limits for logged in users only
                if not user_manager.update_usage(user_id):
                    return JSONResponse(
                        content={
                            "error": "Monthly limit reached", 
                            "upgrade_required": True,
                            "usage": user_manager.get_usage_summary(user_id)
                        }, 
                        status_code=429
                    )
        
        # Load patterns
        patterns = load_custom_patterns()
        pending = load_pending_patterns()

        # Run analysis on the provided text
        analysis_result = analyze_text_content(text_content)

        # Add new patterns to pending (already handled by detect_new_patterns function)
        # The detect_new_patterns function automatically saves new patterns to pending_patterns.json
        
        save_pending_patterns(pending)

        # Update usage for successful analysis
        if user_manager:
            if is_visitor:
                # Create or update visitor record
                user_manager.create_user(user_id)
                user_manager.update_usage(user_id)
            else:
                # Already updated usage above for logged in users
                pass

        # Prepare response data
        risk_count = sum(len(v) for v in analysis_result.get("risks", {}).values())
        good_point_count = sum(len(v) for v in analysis_result.get("good_points", {}).values())
        
        if is_visitor:
            # Visitor response - only show summary
            response_data = {
                "is_visitor": True,
                "visitor_summary": {
                    "risk_count": risk_count,
                    "good_point_count": good_point_count,
                    "analysis_type": "text"
                },
                "message": "Analysis complete! Sign up to see detailed results."
            }
        else:
            # Logged in user response - full analysis
            response_data = {
                "is_visitor": False,
                "analysis": analysis_result,
                "analysis_type": "text"
            }
        
        print(f"DEBUG: Returning response for {'visitor' if is_visitor else 'logged in user'}")
        print(f"DEBUG: Risk count: {risk_count}, Good point count: {good_point_count}")
        
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