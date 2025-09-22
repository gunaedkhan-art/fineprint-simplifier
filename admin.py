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

@router.get("/users", response_class=HTMLResponse)
async def admin_users_page(request: Request, auth: Dict[str, Any] = Depends(check_admin_auth)):
    """User management page"""
    return templates.TemplateResponse("admin_users.html", {"request": request})

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

# User management API endpoints
@router.get("/api/users")
async def get_all_users(auth: Dict[str, Any] = Depends(check_admin_auth)):
    """Get all users with detailed information"""
    try:
        from user_management import user_manager
        
        users_data = []
        for user_id, user_data in user_manager.users.items():
            # Calculate user type
            user_type = "visitor"
            if user_data.get("email"):
                if user_data.get("subscription") == "paid":
                    user_type = "paid"
                else:
                    user_type = "free"
            
            # Get upgrade tracking info
            upgrade_tracking = user_data.get("upgrade_tracking", {})
            
            users_data.append({
                "user_id": user_id,
                "email": user_data.get("email", "No email"),
                "subscription": user_data.get("subscription", "free"),
                "user_type": user_type,
                "created_at": user_data.get("created_at"),
                "last_upload": user_data.get("usage", {}).get("last_upload"),
                "documents_this_month": user_data.get("usage", {}).get("documents_this_month", 0),
                "total_documents": user_data.get("usage", {}).get("total_documents", 0),
                "stripe_customer_id": user_data.get("stripe_customer_id"),
                "stripe_subscription_id": user_data.get("stripe_subscription_id"),
                "subscription_status": user_data.get("subscription_status"),
                "subscription_expires": user_data.get("subscription_expires"),
                "upgrade_attempts": upgrade_tracking.get("upgrade_attempts", 0),
                "abandoned_upgrades": upgrade_tracking.get("abandoned_upgrades", 0),
                "last_upgrade_attempt": upgrade_tracking.get("last_upgrade_attempt"),
                "upgrade_abandoned_at": upgrade_tracking.get("upgrade_abandoned_at")
            })
        
        # Sort by creation date (newest first)
        users_data.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        return {
            "success": True,
            "users": users_data,
            "total_users": len(users_data),
            "visitor_count": len([u for u in users_data if u["user_type"] == "visitor"]),
            "free_count": len([u for u in users_data if u["user_type"] == "free"]),
            "paid_count": len([u for u in users_data if u["user_type"] == "paid"])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading users: {str(e)}")

@router.get("/api/upgrade-abandoners")
async def get_upgrade_abandoners_admin(auth: Dict[str, Any] = Depends(check_admin_auth)):
    """Get users who have abandoned upgrades (for marketing)"""
    try:
        from user_management import user_manager
        
        abandoners = user_manager.get_upgrade_abandoners()
        return {
            "success": True,
            "abandoners": abandoners,
            "count": len(abandoners)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading abandoners: {str(e)}")

@router.post("/api/users/{user_id}/upgrade")
async def admin_upgrade_user(user_id: str, auth: Dict[str, Any] = Depends(check_admin_auth)):
    """Manually upgrade a user to paid tier"""
    try:
        from user_management import user_manager
        
        if user_id not in user_manager.users:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_manager.upgrade_user(user_id, "paid")
        return {"success": True, "message": f"User {user_id} upgraded to paid tier"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error upgrading user: {str(e)}")

@router.post("/api/users/{user_id}/downgrade")
async def admin_downgrade_user(user_id: str, auth: Dict[str, Any] = Depends(check_admin_auth)):
    """Manually downgrade a user to free tier"""
    try:
        from user_management import user_manager
        
        if user_id not in user_manager.users:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_manager.upgrade_user(user_id, "free")
        return {"success": True, "message": f"User {user_id} downgraded to free tier"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downgrading user: {str(e)}")

@router.delete("/api/users/{user_id}")
async def admin_delete_user(user_id: str, auth: Dict[str, Any] = Depends(check_admin_auth)):
    """Delete a user (admin only)"""
    try:
        from user_management import user_manager
        
        if user_id not in user_manager.users:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_manager.delete_user(user_id)
        return {"success": True, "message": f"User {user_id} deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting user: {str(e)}")

@router.get("/api/users/stats")
async def get_user_stats(auth: Dict[str, Any] = Depends(check_admin_auth)):
    """Get comprehensive user statistics"""
    try:
        from user_management import user_manager
        
        stats = {
            "total_users": len(user_manager.users),
            "visitors": 0,
            "free_users": 0,
            "paid_users": 0,
            "users_with_email": 0,
            "users_without_email": 0,
            "total_documents_analyzed": 0,
            "upgrade_abandoners": 0,
            "recent_signups": 0
        }
        
        from datetime import datetime, timedelta
        week_ago = datetime.now() - timedelta(days=7)
        
        for user_id, user_data in user_manager.users.items():
            # Count by type
            if user_data.get("email"):
                stats["users_with_email"] += 1
                if user_data.get("subscription") == "paid":
                    stats["paid_users"] += 1
                else:
                    stats["free_users"] += 1
            else:
                stats["users_without_email"] += 1
                stats["visitors"] += 1
            
            # Count documents
            stats["total_documents_analyzed"] += user_data.get("usage", {}).get("total_documents", 0)
            
            # Count upgrade abandoners
            if user_data.get("upgrade_tracking", {}).get("abandoned_upgrades", 0) > 0:
                stats["upgrade_abandoners"] += 1
            
            # Count recent signups
            created_at = user_data.get("created_at")
            if created_at:
                try:
                    created_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    if created_date > week_ago:
                        stats["recent_signups"] += 1
                except:
                    pass
        
        return {"success": True, "stats": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading stats: {str(e)}")

@router.delete("/api/users/{user_id}/data")
async def delete_user_data(user_id: str, auth: Dict[str, Any] = Depends(check_admin_auth)):
    """GDPR-compliant user data deletion"""
    try:
        from user_management import user_manager
        
        if user_id not in user_manager.users:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Delete user data completely
        user_manager.delete_user(user_id)
        
        return {"success": True, "message": f"All data for user {user_id} has been deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting user data: {str(e)}")

@router.get("/api/users/{user_id}/data")
async def export_user_data(user_id: str, auth: Dict[str, Any] = Depends(check_admin_auth)):
    """Export user data for GDPR compliance"""
    try:
        from user_management import user_manager
        
        if user_id not in user_manager.users:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_data = user_manager.users[user_id]
        
        # Return user data (excluding sensitive fields like password_hash)
        export_data = {
            "user_id": user_id,
            "email": user_data.get("email"),
            "subscription": user_data.get("subscription"),
            "created_at": user_data.get("created_at"),
            "usage": user_data.get("usage"),
            "upgrade_tracking": user_data.get("upgrade_tracking"),
            "stripe_customer_id": user_data.get("stripe_customer_id"),
            "subscription_status": user_data.get("subscription_status")
        }
        
        return {"success": True, "user_data": export_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting user data: {str(e)}")
