# admin.py - Admin area functionality with secure authentication


from fastapi import APIRouter, Request, Form, HTTPException, Depends, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
import json
import os
from typing import Optional, Dict, Any

# Import existing modules
from matcher import load_custom_patterns, load_pending_patterns, save_pending_patterns
from core_patterns import RISK_PATTERNS, GOOD_PATTERNS

# Import security modules
from auth import auth_manager, get_current_admin, create_admin_password_hash

router = APIRouter(prefix="/admin")
templates = Jinja2Templates(directory="templates")

def check_admin_auth(request: Request) -> Dict[str, Any]:
    """Check if user is authenticated as admin using JWT from cookie"""
    token = request.cookies.get("admin_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
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
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.get("/", response_class=HTMLResponse)
async def admin_root(request: Request):
    """Redirect admin root to login"""
    return RedirectResponse(url="/admin/login", status_code=302)

@router.get("/login", response_class=HTMLResponse)
async def admin_login_page(request: Request):
    """Admin login page"""
    return templates.TemplateResponse("admin_login.html", {"request": request})

@router.post("/login")
async def admin_login(request: Request, username: str = Form(...), password: str = Form(...)):
    """Handle admin login with JWT authentication"""
    try:
        # Authenticate user
        token = auth_manager.authenticate_admin(username, password)
        
        if token:
            # Create response with JWT token in secure cookie
            response = RedirectResponse(url="/admin/dashboard", status_code=302)
            response.set_cookie(
                key="admin_token",
                value=token,
                httponly=True,
                secure=True,  # Only send over HTTPS
                samesite="strict",
                max_age=3600  # 1 hour
            )
            return response
        else:
            return templates.TemplateResponse("admin_login.html", {
                "request": request, 
                "error": "Invalid credentials"
            })
    except Exception as e:
        return templates.TemplateResponse("admin_login.html", {
            "request": request, 
            "error": "Login failed. Please try again."
        })

@router.get("/logout")
async def admin_logout(request: Request):
    """Handle admin logout"""
    response = RedirectResponse(url="/admin/login", status_code=302)
    response.delete_cookie("admin_token")
    return response

@router.get("/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request, auth: Dict[str, Any] = Depends(check_admin_auth)):
    """Admin dashboard"""
    try:
        # Load all patterns for overview
        custom_patterns = load_custom_patterns()
        pending_patterns = load_pending_patterns()
        
        # Count patterns
        custom_risk_count = sum(len(patterns) for patterns in custom_patterns.get("risks", {}).values())
        custom_good_count = sum(len(patterns) for patterns in custom_patterns.get("good_points", {}).values())
        
        # Handle mixed format in pending patterns (some are dicts with "patterns" key, some are lists)
        pending_risk_count = 0
        for data in pending_patterns.get("risks", {}).values():
            if isinstance(data, dict) and "patterns" in data:
                pending_risk_count += len(data["patterns"])
            elif isinstance(data, list):
                pending_risk_count += len(data)
        
        pending_good_count = 0
        for data in pending_patterns.get("good_points", {}).values():
            if isinstance(data, dict) and "patterns" in data:
                pending_good_count += len(data["patterns"])
            elif isinstance(data, list):
                pending_good_count += len(data)
        
        stats = {
            "core_risk_patterns": len(RISK_PATTERNS),
            "core_good_patterns": len(GOOD_PATTERNS),
            "custom_risk_patterns": custom_risk_count,
            "custom_good_patterns": custom_good_count,
            "pending_risk_patterns": pending_risk_count,
            "pending_good_patterns": pending_good_count,
            "total_custom_categories": len(custom_patterns.get("risks", {})) + len(custom_patterns.get("good_points", {})),
            "total_pending_categories": len(pending_patterns.get("risks", {})) + len(pending_patterns.get("good_points", {}))
        }
        
        return templates.TemplateResponse("admin_dashboard.html", {
            "request": request,
            "stats": stats
        })
    except Exception as e:
        # Return a simple error page if there's an issue
        return templates.TemplateResponse("admin_dashboard.html", {
            "request": request,
            "stats": {
                "core_risk_patterns": 0,
                "core_good_patterns": 0,
                "custom_risk_patterns": 0,
                "custom_good_patterns": 0,
                "pending_risk_patterns": 0,
                "pending_good_patterns": 0,
                "total_custom_categories": 0,
                "total_pending_categories": 0
            },
            "error": f"Error loading dashboard: {str(e)}"
        })

@router.get("/patterns", response_class=HTMLResponse)
async def admin_patterns_page(request: Request, auth: Dict[str, Any] = Depends(check_admin_auth)):
    """Pattern management page"""
    return templates.TemplateResponse("admin_patterns.html", {"request": request})

@router.get("/pending", response_class=HTMLResponse)
async def admin_pending_page(request: Request, auth: Dict[str, Any] = Depends(check_admin_auth)):
    """Pending patterns review page"""
    return templates.TemplateResponse("admin_pending.html", {"request": request})

@router.get("/search", response_class=HTMLResponse)
async def admin_search_page(request: Request, auth: Dict[str, Any] = Depends(check_admin_auth)):
    """Pattern search page"""
    return templates.TemplateResponse("admin_search.html", {"request": request})

# API endpoints for admin functionality
@router.get("/api/custom-patterns")
async def get_custom_patterns(auth: Dict[str, Any] = Depends(check_admin_auth)):
    """Get all custom patterns"""
    return load_custom_patterns()

@router.get("/api/pending-patterns")
async def get_pending_patterns(auth: Dict[str, Any] = Depends(check_admin_auth)):
    """Get all pending patterns"""
    return load_pending_patterns()

@router.get("/api/core-patterns")
async def get_core_patterns(auth: Dict[str, Any] = Depends(check_admin_auth)):
    """Get all core patterns"""
    return {
        "risks": RISK_PATTERNS,
        "good_points": GOOD_PATTERNS
    }

@router.post("/api/score-pattern")
async def score_pattern(
    pattern_text: str = Form(...),
    category: str = Form(...),
    pattern_type: str = Form(...),
    score: int = Form(...),
    auth: Dict[str, Any] = Depends(check_admin_auth)
):
    """Score a pending pattern and move it to custom patterns"""
    try:
        pending_patterns = load_pending_patterns()
        custom_patterns = load_custom_patterns()
        
        # Find and remove from pending
        found = False
        for ptype in ["risks", "good_points"]:
            if ptype in pending_patterns and category in pending_patterns[ptype]:
                data = pending_patterns[ptype][category]
                if isinstance(data, dict) and "patterns" in data:
                    patterns = data["patterns"]
                    if pattern_text in patterns:
                        patterns.remove(pattern_text)
                        found = True
                        break
                elif isinstance(data, list):
                    if pattern_text in data:
                        data.remove(pattern_text)
                        found = True
                        break
        
        if not found:
            raise HTTPException(status_code=404, detail="Pattern not found in pending")
        
        # Add to custom patterns
        if pattern_type not in custom_patterns:
            custom_patterns[pattern_type] = {}
        
        if category not in custom_patterns[pattern_type]:
            custom_patterns[pattern_type][category] = []
        
        custom_patterns[pattern_type][category].append(pattern_text)
        
        # Save both files
        with open("custom_patterns.json", "w") as f:
            json.dump(custom_patterns, f, indent=2)
        
        save_pending_patterns(pending_patterns)
        
        return {"success": True, "message": "Pattern scored and moved to custom patterns"}
    
    except Exception as e:
        print(f"Error in score_pattern: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.delete("/api/reject-pattern")
async def reject_pattern(
    pattern_text: str = Form(...),
    category: str = Form(...),
    pattern_type: str = Form(...),
    auth: Dict[str, Any] = Depends(check_admin_auth)
):
    """Reject a pending pattern"""
    try:
        pending_patterns = load_pending_patterns()
        
        # Find and remove from pending
        found = False
        for ptype in ["risks", "good_points"]:
            if ptype in pending_patterns and category in pending_patterns[ptype]:
                data = pending_patterns[ptype][category]
                if isinstance(data, dict) and "patterns" in data:
                    patterns = data["patterns"]
                    if pattern_text in patterns:
                        patterns.remove(pattern_text)
                        found = True
                        break
                elif isinstance(data, list):
                    if pattern_text in data:
                        data.remove(pattern_text)
                        found = True
                        break
        
        if not found:
            raise HTTPException(status_code=404, detail="Pattern not found in pending")
        
        save_pending_patterns(pending_patterns)
        
        return {"success": True, "message": "Pattern rejected"}
    
    except Exception as e:
        print(f"Error in reject_pattern: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/api/add-pattern")
async def add_pattern(
    pattern_text: str = Form(...),
    category: str = Form(...),
    pattern_type: str = Form(...),
    score: int = Form(...),
    auth: Dict[str, Any] = Depends(check_admin_auth)
):
    """Add a new pattern directly to custom patterns"""
    custom_patterns = load_custom_patterns()
    
    if pattern_type not in custom_patterns:
        custom_patterns[pattern_type] = {}
    
    if category not in custom_patterns[pattern_type]:
        custom_patterns[pattern_type][category] = []
    
    if pattern_text not in custom_patterns[pattern_type][category]:
        custom_patterns[pattern_type][category].append(pattern_text)
    
    with open("custom_patterns.json", "w") as f:
        json.dump(custom_patterns, f, indent=2)
    
    return {"success": True, "message": "Pattern added successfully"}
