# user_management.py - User management and usage tracking

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pricing_config import FREE_TIER_LIMITS, PAID_TIER_FEATURES

class UserManager:
    def __init__(self, users_file: str = "users.json"):
        self.users_file = users_file
        self.users = self._load_users()
    
    def _load_users(self) -> Dict:
        """Load users from JSON file"""
        if os.path.exists(self.users_file):
            try:
                with open(self.users_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return {}
        return {}
    
    def _save_users(self):
        """Save users to JSON file"""
        with open(self.users_file, 'w') as f:
            json.dump(self.users, f, indent=2, default=str)
    
    def create_user(self, user_id: str, email: str = None) -> Dict:
        """Create a new user with free tier"""
        if user_id not in self.users:
            self.users[user_id] = {
                "email": email,
                "subscription": "free",
                "created_at": datetime.now().isoformat(),
                "usage": {
                    "current_month": datetime.now().strftime("%Y-%m"),
                    "documents_this_month": 0,
                    "total_documents": 0,
                    "last_upload": None
                }
            }
            self._save_users()
        return self.users[user_id]
    
    def get_user(self, user_id: str) -> Optional[Dict]:
        """Get user information"""
        if user_id not in self.users:
            return None
        return self.users[user_id]
    
    def update_usage(self, user_id: str) -> bool:
        """Update user usage and check if they can upload"""
        print(f"DEBUG: update_usage called for user_id: {user_id}")
        
        if user_id not in self.users:
            print(f"DEBUG: Creating new user for {user_id}")
            self.create_user(user_id)
        
        user = self.users[user_id]
        current_month = datetime.now().strftime("%Y-%m")
        
        print(f"DEBUG: User data: {user}")
        print(f"DEBUG: Current month: {current_month}, User month: {user['usage']['current_month']}")
        
        # Reset monthly usage if it's a new month
        if user["usage"]["current_month"] != current_month:
            print(f"DEBUG: Resetting monthly usage for new month")
            user["usage"]["current_month"] = current_month
            user["usage"]["documents_this_month"] = 0
        
        # Check if user can upload
        print(f"DEBUG: Subscription: {user['subscription']}")
        if user["subscription"] == "paid":
            print(f"DEBUG: Paid user - allowing upload")
            # Paid users can always upload
            pass
        elif user["subscription"] == "free":
            print(f"DEBUG: Free user check - email: {user.get('email')}, docs this month: {user['usage']['documents_this_month']}")
            # Allow upload if user has no email (visitor) or hasn't reached limit
            if user.get("email") and user["usage"]["documents_this_month"] >= FREE_TIER_LIMITS["documents_per_month"]:
                print(f"DEBUG: Free user with email has reached limit - denying upload")
                return False
        else:
            print(f"DEBUG: Unknown subscription type: {user['subscription']}")
            return False
        
        print(f"DEBUG: Allowing upload - updating usage")
        # Update usage
        user["usage"]["documents_this_month"] += 1
        user["usage"]["total_documents"] += 1
        user["usage"]["last_upload"] = datetime.now().isoformat()
        
        self._save_users()
        return True
    
    def revert_usage(self, user_id: str):
        """Revert the usage count (for failed uploads)"""
        if user_id in self.users:
            user = self.users[user_id]
            # Revert the usage increase
            user["usage"]["documents_this_month"] = max(0, user["usage"]["documents_this_month"] - 1)
            user["usage"]["total_documents"] = max(0, user["usage"]["total_documents"] - 1)
            self._save_users()
    
    def can_use_feature(self, user_id: str, feature: str) -> bool:
        """Check if user can use a specific feature"""
        if user_id not in self.users:
            return False
        
        user = self.users[user_id]
        
        # Free tier features
        if feature in FREE_TIER_LIMITS["features"]:
            return True
        
        # Paid tier features
        if feature in PAID_TIER_FEATURES:
            return user["subscription"] == "paid"
        
        return False
    
    def upgrade_user(self, user_id: str, subscription_type: str = "paid"):
        """Upgrade user to paid tier"""
        if user_id not in self.users:
            self.create_user(user_id)
        
        self.users[user_id]["subscription"] = subscription_type
        self._save_users()
    
    def get_usage_summary(self, user_id: str) -> Dict:
        """Get user usage summary"""
        print(f"DEBUG: get_usage_summary called for user_id: {user_id}")
        
        if user_id not in self.users:
            print(f"DEBUG: User not found")
            return {"error": "User not found"}
        
        user = self.users[user_id]
        current_month = datetime.now().strftime("%Y-%m")
        
        print(f"DEBUG: User data: {user}")
        
        # Reset monthly usage if it's a new month
        if user["usage"]["current_month"] != current_month:
            print(f"DEBUG: Resetting monthly usage for new month")
            user["usage"]["current_month"] = current_month
            user["usage"]["documents_this_month"] = 0
            self._save_users()
        
        # For visitors (no email), allow uploads
        can_upload = True
        if user["subscription"] == "free" and user.get("email"):
            can_upload = user["usage"]["documents_this_month"] < FREE_TIER_LIMITS["documents_per_month"]
        elif user["subscription"] == "paid":
            can_upload = True
        
        result = {
            "subscription": user["subscription"],
            "email": user.get("email"),
            "documents_this_month": user["usage"]["documents_this_month"],
            "total_documents": user["usage"]["total_documents"],
            "monthly_limit": FREE_TIER_LIMITS["documents_per_month"] if user["subscription"] == "free" else "unlimited",
            "can_upload": can_upload
        }
        
        print(f"DEBUG: Returning usage summary: {result}")
        return result

    def reset_user_usage(self, user_id: str):
        """Reset user usage for testing purposes"""
        if user_id in self.users:
            user = self.users[user_id]
            user["usage"]["documents_this_month"] = 0
            user["usage"]["total_documents"] = 0
            user["usage"]["last_upload"] = None
            user["email"] = None  # Make them a visitor again
            user["subscription"] = "free"  # Reset to free tier
            self._save_users()
            print(f"DEBUG: Reset usage and subscription for user {user_id}")
        else:
            print(f"DEBUG: User {user_id} not found for reset")

# Global user manager instance
user_manager = UserManager()
