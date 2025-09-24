# user_management.py - User management and usage tracking

import json
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
    
    def create_user(self, user_id: str, email: str = None, password_hash: str = None, username: str = None) -> Dict:
        """Create a new user with free tier"""
        if user_id not in self.users:
            self.users[user_id] = {
                "username": username,
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
            self._save_users()
        return self.users[user_id]
    
    def create_authenticated_user(self, username: str, email: str, password_hash: str) -> Dict:
        """Create a new authenticated user"""
        # Use username for user ID generation for better privacy
        safe_username = username.lower().replace(' ', '_').replace('-', '_')
        user_id = f"user_{safe_username}_{int(datetime.now().timestamp())}"
        return self.create_user(user_id, email, password_hash, username=username)
    
    def authenticate_user(self, email: str, password: str) -> Optional[Dict]:
        """Authenticate a user with email and password"""
        # Find user by email
        user = None
        for user_id, user_data in self.users.items():
            if user_data.get("email") == email:
                user = user_data
                user["user_id"] = user_id
                break
        
        if not user:
            return None
        
        # Check password
        if not user.get("password_hash"):
            return None
        
        try:
            from auth import auth_manager
            if auth_manager.verify_password(password, user["password_hash"]):
                return user
        except:
            pass
        
        return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email address"""
        for user_id, user_data in self.users.items():
            if user_data.get("email") == email:
                user_data["user_id"] = user_id
                return user_data
        return None
    
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Get user by username"""
        for user_id, user_data in self.users.items():
            if user_data.get("username") == username:
                user_data["user_id"] = user_id
                return user_data
        return None
    
    def get_user(self, user_id: str) -> Optional[Dict]:
        """Get user information"""
        if user_id not in self.users:
            return None
        return self.users[user_id]
    
    def is_visitor(self, user_id: str) -> bool:
        """Check if user is a visitor (no email)"""
        user = self.get_user(user_id)
        return user is not None and not user.get("email")
    
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
        print(f"DEBUG: Subscription: {user['subscription']}, Email: {user.get('email')}")
        
        # Visitors (no email) can always upload once
        if not user.get("email"):
            print(f"DEBUG: Visitor - allowing upload")
            # Update usage
            user["usage"]["documents_this_month"] += 1
            user["usage"]["total_documents"] += 1
            user["usage"]["last_upload"] = datetime.now().isoformat()
            self._save_users()
            return True
        
        # Logged in users check limits
        if user["subscription"] == "paid":
            print(f"DEBUG: Paid user - allowing upload")
            # Paid users can always upload
            user["usage"]["documents_this_month"] += 1
            user["usage"]["total_documents"] += 1
            user["usage"]["last_upload"] = datetime.now().isoformat()
            self._save_users()
            return True
        elif user["subscription"] == "free":
            print(f"DEBUG: Free user check - docs this month: {user['usage']['documents_this_month']}")
            if user["usage"]["documents_this_month"] >= FREE_TIER_LIMITS["documents_per_month"]:
                print(f"DEBUG: Free user has reached limit - denying upload")
                return False
            else:
                print(f"DEBUG: Free user - allowing upload")
                user["usage"]["documents_this_month"] += 1
                user["usage"]["total_documents"] += 1
                user["usage"]["last_upload"] = datetime.now().isoformat()
                self._save_users()
                return True
        else:
            print(f"DEBUG: Unknown subscription type: {user['subscription']}")
            return False
    
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
    
    def update_stripe_subscription(self, user_id: str, customer_id: str, subscription_id: str, status: str, expires_at: int = None):
        """Update user's Stripe subscription information"""
        if user_id not in self.users:
            self.create_user(user_id)
        
        user = self.users[user_id]
        user["stripe_customer_id"] = customer_id
        user["stripe_subscription_id"] = subscription_id
        user["subscription_status"] = status
        
        if expires_at:
            user["subscription_expires"] = datetime.fromtimestamp(expires_at).isoformat()
        
        # Update subscription type based on status
        if status in ["active", "trialing"]:
            user["subscription"] = "paid"
        else:
            user["subscription"] = "free"
        
        self._save_users()
    
    def cancel_stripe_subscription(self, user_id: str):
        """Cancel user's Stripe subscription"""
        if user_id in self.users:
            user = self.users[user_id]
            user["subscription"] = "free"
            user["subscription_status"] = "canceled"
            user["stripe_subscription_id"] = None
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
        
        # Determine if user can upload
        can_upload = True
        if not user.get("email"):
            # Visitors can always upload once
            can_upload = True
        elif user["subscription"] == "free":
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
            # Remove any inconsistent fields
            if "email_consent" in user:
                del user["email_consent"]
            self._save_users()
            print(f"DEBUG: Reset usage and subscription for user {user_id}")
        else:
            print(f"DEBUG: User {user_id} not found for reset")
    
    def delete_user(self, user_id: str):
        """Delete a user completely for testing purposes"""
        if user_id in self.users:
            del self.users[user_id]
            self._save_users()
            print(f"DEBUG: Deleted user {user_id}")
        else:
            print(f"DEBUG: User {user_id} not found for deletion")
    
    def track_upgrade_attempt(self, user_id: str):
        """Track when a user attempts to upgrade"""
        if user_id not in self.users:
            self.create_user(user_id)
        
        user = self.users[user_id]
        if "upgrade_tracking" not in user:
            user["upgrade_tracking"] = {
                "upgrade_attempts": 0,
                "last_upgrade_attempt": None,
                "abandoned_upgrades": 0,
                "upgrade_abandoned_at": None
            }
        
        user["upgrade_tracking"]["upgrade_attempts"] += 1
        user["upgrade_tracking"]["last_upgrade_attempt"] = datetime.now().isoformat()
        self._save_users()
    
    def track_upgrade_abandonment(self, user_id: str):
        """Track when a user abandons the upgrade process"""
        if user_id in self.users:
            user = self.users[user_id]
            if "upgrade_tracking" not in user:
                user["upgrade_tracking"] = {
                    "upgrade_attempts": 0,
                    "last_upgrade_attempt": None,
                    "abandoned_upgrades": 0,
                    "upgrade_abandoned_at": None
                }
            
            user["upgrade_tracking"]["abandoned_upgrades"] += 1
            user["upgrade_tracking"]["upgrade_abandoned_at"] = datetime.now().isoformat()
            self._save_users()
    
    def get_upgrade_abandoners(self) -> List[Dict]:
        """Get list of users who have abandoned upgrades (for marketing)"""
        abandoners = []
        for user_id, user_data in self.users.items():
            if (user_data.get("upgrade_tracking", {}).get("abandoned_upgrades", 0) > 0 and 
                user_data.get("subscription") == "free" and 
                user_data.get("email")):
                abandoners.append({
                    "user_id": user_id,
                    "email": user_data.get("email"),
                    "abandoned_upgrades": user_data.get("upgrade_tracking", {}).get("abandoned_upgrades", 0),
                    "last_upgrade_attempt": user_data.get("upgrade_tracking", {}).get("last_upgrade_attempt"),
                    "upgrade_abandoned_at": user_data.get("upgrade_tracking", {}).get("upgrade_abandoned_at")
                })
        return abandoners

# Global user manager instance
user_manager = UserManager()
