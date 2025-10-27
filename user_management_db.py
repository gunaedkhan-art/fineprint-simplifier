# user_management_db.py - Database-backed user management and usage tracking

import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

try:
    from pricing_config import FREE_TIER_LIMITS, PAID_TIER_FEATURES
except ImportError:
    # Fallback configuration if pricing_config is not available
    FREE_TIER_LIMITS = {
        "documents_per_month": 3,
        "features": [
            "plain_english_summary",
            "basic_risk_detection", 
            "basic_good_points_detection"
        ]
    }
    PAID_TIER_FEATURES = [
        "unlimited_documents",
        "risk_score_badges",
        "side_by_side_comparison",
        "export_pdf",
        "export_word", 
        "export_excel",
        "advanced_analytics",
        "priority_support"
    ]

from database import db_manager

class UserManager:
    def __init__(self):
        """Initialize database-backed user manager"""
        self.db = db_manager
        print("✅ UserManager initialized with database backend")
    
    def create_user(self, user_id: str, email: str = None, password_hash: str = None, username: str = None) -> Dict:
        """Create a new user with free tier"""
        if email and password_hash and username:
            # Create authenticated user
            return self.create_authenticated_user(username, email, password_hash)[1]
        else:
            # Create anonymous user
            user_data = {
                "username": username or f"user_{user_id[:8]}",
                "email": email,
                "password_hash": password_hash,
                "subscription": "free",
                "created_at": datetime.now().isoformat(),
                "stripe_customer_id": None,
                "stripe_subscription_id": None,
                "subscription_status": "free",
                "subscription_expires": None,
                "usage": {
                    "current_month": datetime.now().strftime("%Y-%m"),
                    "documents_this_month": 0,
                    "total_documents": 0,
                    "last_upload": None
                },
                "upgrade_tracking": {
                    "upgrade_attempts": 0,
                    "last_upgrade_attempt": None,
                    "abandoned_upgrades": 0,
                    "upgrade_abandoned_at": None
                }
            }
            return self.db.create_user(user_id, email or "", password_hash or "", username or f"user_{user_id[:8]}")
    
    def create_authenticated_user(self, username: str, email: str, password_hash: str) -> tuple:
        """Create a new authenticated user"""
        user_id = f"user_{username}_{int(datetime.now().timestamp())}"
        
        user_data = self.db.create_user(user_id, email, password_hash, username)
        return user_id, user_data
    
    def get_user(self, user_id: str) -> Optional[Dict]:
        """Get user by ID"""
        return self.db.get_user(user_id)
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        return self.db.get_user_by_email(email)
    
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Get user by username"""
        return self.db.get_user_by_username(username)
    
    def authenticate_user(self, email: str, password: str) -> Optional[Dict]:
        """Authenticate user with email and password"""
        print(f"🔐 AUTHENTICATE: Attempting to authenticate email: {email}")
        user = self.db.get_user_by_email(email)
        print(f"🔐 AUTHENTICATE: User found: {user is not None}")
        
        if not user:
            print(f"🔐 AUTHENTICATE: No user found with email: {email}")
            return None
        
        print(f"🔐 AUTHENTICATE: User ID: {user.get('user_id')}, Has password_hash: {bool(user.get('password_hash'))}")
        
        # Import auth_manager here to avoid circular imports
        from auth import auth_manager
        if auth_manager:
            password_valid = auth_manager.verify_password(password, user.get("password_hash"))
            print(f"🔐 AUTHENTICATE: Password verification result: {password_valid}")
            if password_valid:
                return user
        else:
            print(f"🔐 AUTHENTICATE: auth_manager is None")
        
        print(f"🔐 AUTHENTICATE: Authentication failed for email: {email}")
        return None
    
    def update_password(self, email: str, new_password_hash: str) -> bool:
        """Update user password"""
        from auth import auth_manager
        user = self.db.get_user_by_email(email)
        if user:
            return self.db.update_user(user["user_id"], password_hash=new_password_hash)
        return False
    
    def can_upload_document(self, user_id: str) -> bool:
        """Check if user can upload a document based on their subscription and usage"""
        user = self.get_user(user_id)
        if not user:
            return False
        
        # Anonymous users can always upload (they get limited analysis)
        if not user.get("email"):
            return True
        
        # Logged in users check limits
        if user["subscription"] == "premium":
            return True
        elif user["subscription"] == "free":
            current_month = datetime.now().strftime("%Y-%m")
            usage = user.get("usage", {})
            
            # Reset monthly usage if it's a new month
            if usage.get("current_month") != current_month:
                usage["current_month"] = current_month
                usage["documents_this_month"] = 0
                self.db.update_usage(user_id, usage)
            
            # Check if user has exceeded free tier limit
            if usage.get("documents_this_month", 0) >= FREE_TIER_LIMITS["documents_per_month"]:
                return False
            
            return True
        else:
            print(f"DEBUG: Unknown subscription type: {user['subscription']}")
            return False
    
    def record_document_upload(self, user_id: str) -> bool:
        """Record a document upload for usage tracking"""
        print(f"📊 record_document_upload called for user: {user_id}")
        user = self.get_user(user_id)
        if not user:
            print(f"📊 User not found: {user_id}")
            return False
        
        usage = user.get("usage", {})
        current_month = datetime.now().strftime("%Y-%m")
        print(f"📊 Current usage before update: {usage}")
        
        # Reset monthly usage if it's a new month
        if usage.get("current_month") != current_month:
            usage["current_month"] = current_month
            usage["documents_this_month"] = 0
            print(f"📊 Reset monthly usage for new month: {current_month}")
        
        # Update usage
        old_count = usage.get("documents_this_month", 0)
        usage["documents_this_month"] = old_count + 1
        usage["total_documents"] = usage.get("total_documents", 0) + 1
        usage["last_upload"] = datetime.now().isoformat()
        
        print(f"📊 Updated usage: {usage}")
        result = self.db.update_usage(user_id, usage)
        print(f"📊 Database update result: {result}")
        return result
    
    def can_use_feature(self, user_id: str, feature: str) -> bool:
        """Check if user can use a specific feature"""
        user = self.get_user(user_id)
        if not user:
            return False
        
        if user["subscription"] == "premium":
            return True
        elif user["subscription"] == "free":
            return feature in FREE_TIER_LIMITS.get("features", [])
        
        return False
    
    def update_usage(self, user_id: str) -> bool:
        """Update user usage (alias for record_document_upload)"""
        return self.record_document_upload(user_id)
    
    def get_user_usage(self, user_id: str) -> Dict:
        """Get user usage (alias for get_usage_summary)"""
        return self.get_usage_summary(user_id)
    
    def set_subscription(self, user_id: str, subscription_type: str):
        """Set user subscription type"""
        self.db.update_user(user_id, subscription=subscription_type)
    
    def update_stripe_subscription(self, user_id: str, customer_id: str, subscription_id: str, status: str, expires_at: int = None):
        """Update user's Stripe subscription information"""
        user = self.get_user(user_id)
        if not user:
            return
        
        updates = {
            "stripe_customer_id": customer_id,
            "stripe_subscription_id": subscription_id,
            "subscription_status": status
        }
        
        if expires_at:
            expires_date = datetime.fromtimestamp(expires_at)
            updates["subscription_expires"] = expires_date
        
        if status == "active":
            updates["subscription"] = "premium"
        else:
            updates["subscription"] = "free"
        
        self.db.update_user(user_id, **updates)
    
    def cancel_stripe_subscription(self, user_id: str):
        """Cancel user's Stripe subscription"""
        self.db.update_user(user_id, 
                           subscription="free",
                           subscription_status="canceled",
                           stripe_subscription_id=None)
    
    def get_usage_summary(self, user_id: str) -> Dict:
        """Get user usage summary"""
        user = self.get_user(user_id)
        if not user:
            return {"error": "User not found"}
        
        usage = user.get("usage", {})
        current_month = datetime.now().strftime("%Y-%m")
        
        # Reset monthly usage if it's a new month
        if usage.get("current_month") != current_month:
            usage["current_month"] = current_month
            usage["documents_this_month"] = 0
            self.db.update_usage(user_id, usage)
        
        # Determine if user can upload
        can_upload = True
        if user["subscription"] == "free":
            can_upload = usage.get("documents_this_month", 0) < FREE_TIER_LIMITS["documents_per_month"]
        
        return {
            "subscription": user["subscription"],
            "documents_this_month": usage.get("documents_this_month", 0),
            "total_documents": usage.get("total_documents", 0),
            "monthly_limit": FREE_TIER_LIMITS["documents_per_month"] if user["subscription"] == "free" else "unlimited",
            "can_upload": can_upload,
            "last_upload": usage.get("last_upload"),
            "features": PAID_TIER_FEATURES if user["subscription"] == "premium" else FREE_TIER_LIMITS["features"]
        }
    
    def reset_user_usage(self, user_id: str):
        """Reset user usage for testing purposes"""
        user = self.get_user(user_id)
        if user:
            usage = {
                "current_month": datetime.now().strftime("%Y-%m"),
                "documents_this_month": 0,
                "total_documents": 0,
                "last_upload": None
            }
            self.db.update_usage(user_id, usage)
            print(f"DEBUG: Reset usage for user {user_id}")
        else:
            print(f"DEBUG: User {user_id} not found for reset")
    
    def delete_user(self, user_id: str):
        """Delete a user completely for testing purposes"""
        success = self.db.delete_user(user_id)
        if success:
            print(f"DEBUG: Deleted user {user_id}")
        else:
            print(f"DEBUG: User {user_id} not found for deletion")
    
    def track_upgrade_attempt(self, user_id: str):
        """Track when a user attempts to upgrade"""
        user = self.get_user(user_id)
        if user:
            upgrade_tracking = user.get("upgrade_tracking", {})
            upgrade_tracking["upgrade_attempts"] = upgrade_tracking.get("upgrade_attempts", 0) + 1
            upgrade_tracking["last_upgrade_attempt"] = datetime.now().isoformat()
            self.db.update_upgrade_tracking(user_id, upgrade_tracking)
    
    def track_upgrade_abandonment(self, user_id: str):
        """Track when a user abandons the upgrade process"""
        user = self.get_user(user_id)
        if user:
            upgrade_tracking = user.get("upgrade_tracking", {})
            upgrade_tracking["abandoned_upgrades"] = upgrade_tracking.get("abandoned_upgrades", 0) + 1
            upgrade_tracking["upgrade_abandoned_at"] = datetime.now().isoformat()
            self.db.update_upgrade_tracking(user_id, upgrade_tracking)
    
    def get_upgrade_abandoners(self) -> List[Dict]:
        """Get list of users who have abandoned upgrades (for marketing)"""
        # This would require a more complex query in a real implementation
        # For now, return empty list
        return []
    
    def get_all_users(self) -> List[Dict]:
        """Get all users (for admin purposes)"""
        # This would require a more complex query in a real implementation
        # For now, return empty list
        return []
    
    @property
    def users(self) -> Dict:
        """Compatibility property to maintain interface with existing code"""
        # Return empty dict for compatibility
        return {}
