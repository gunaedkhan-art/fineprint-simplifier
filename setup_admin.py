#!/usr/bin/env python3
"""
Admin Setup Utility

This script helps you set up a secure admin password hash for production.
Run this script to generate a password hash that you can use in your environment variables.
"""

import os
import sys
from auth import create_admin_password_hash

def main():
    print("🔐 Admin Password Setup Utility")
    print("=" * 40)
    
    # Get admin username
    username = input("Enter admin username (default: admin): ").strip()
    if not username:
        username = "admin"
    
    # Get password
    import getpass
    password = getpass.getpass("Enter admin password: ")
    if not password:
        print("❌ Password cannot be empty!")
        sys.exit(1)
    
    # Confirm password
    confirm_password = getpass.getpass("Confirm admin password: ")
    if password != confirm_password:
        print("❌ Passwords do not match!")
        sys.exit(1)
    
    # Generate hash
    password_hash = create_admin_password_hash(password)
    
    print("\n✅ Admin credentials generated successfully!")
    print("\n📋 Environment Variables to Set:")
    print("=" * 40)
    print(f"ADMIN_USERNAME={username}")
    print(f"ADMIN_PASSWORD_HASH={password_hash}")
    print(f"JWT_SECRET_KEY={os.environ.get('JWT_SECRET_KEY', 'CHANGE_THIS_IN_PRODUCTION')}")
    print(f"JWT_EXPIRE_MINUTES=60")
    print(f"FORCE_HTTPS=true")
    
    print("\n🚀 For Production Deployment:")
    print("=" * 40)
    print("Heroku:")
    print(f"  heroku config:set ADMIN_USERNAME={username}")
    print(f"  heroku config:set ADMIN_PASSWORD_HASH={password_hash}")
    print(f"  heroku config:set JWT_SECRET_KEY=your-secure-jwt-secret")
    print(f"  heroku config:set FORCE_HTTPS=true")
    
    print("\nRailway:")
    print(f"  ADMIN_USERNAME={username}")
    print(f"  ADMIN_PASSWORD_HASH={password_hash}")
    print(f"  JWT_SECRET_KEY=your-secure-jwt-secret")
    print(f"  FORCE_HTTPS=true")
    
    print("\n⚠️  Security Notes:")
    print("=" * 40)
    print("• Keep these credentials secure and never commit them to version control")
    print("• Use a strong, unique JWT_SECRET_KEY in production")
    print("• Enable HTTPS in production (FORCE_HTTPS=true)")
    print("• Consider using a password manager to store these credentials")
    
    # Test the hash
    print("\n🧪 Testing password hash...")
    from auth import auth_manager
    test_token = auth_manager.authenticate_admin(username, password)
    if test_token:
        print("✅ Password hash test successful!")
    else:
        print("❌ Password hash test failed!")

if __name__ == "__main__":
    main()
