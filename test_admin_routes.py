#!/usr/bin/env python3
"""
Test script to verify admin routes are working
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.getcwd())

def test_admin_import():
    print("🧪 Testing Admin Router Import")
    print("=" * 40)
    
    try:
        from admin import router
        print("✅ Admin router imported successfully")
        print(f"   Router prefix: {router.prefix}")
        print(f"   Number of routes: {len(router.routes)}")
        
        # List all routes
        print("\n📋 Admin Routes:")
        for route in router.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                methods = ', '.join(route.methods)
                print(f"   {methods} {route.path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Admin router import failed: {e}")
        return False

def test_main_app():
    print("\n🧪 Testing Main App Import")
    print("=" * 40)
    
    try:
        # Try to import just the app creation part
        from fastapi import FastAPI
        
        # Create a minimal app to test
        app = FastAPI()
        
        # Try to import admin router
        from admin import router as admin_router
        app.include_router(admin_router)
        
        print("✅ Main app with admin router created successfully")
        
        # Check if routes are registered
        admin_routes = [route for route in app.routes if hasattr(route, 'path') and route.path.startswith('/admin')]
        print(f"   Admin routes registered: {len(admin_routes)}")
        
        for route in admin_routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                methods = ', '.join(route.methods)
                print(f"   {methods} {route.path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Main app test failed: {e}")
        return False

def test_route_paths():
    print("\n🧪 Testing Route Paths")
    print("=" * 40)
    
    expected_paths = [
        "/admin/",
        "/admin/login", 
        "/admin/dashboard",
        "/admin/pending",
        "/admin/patterns",
        "/admin/search"
    ]
    
    try:
        from admin import router
        
        actual_paths = []
        for route in router.routes:
            if hasattr(route, 'path'):
                actual_paths.append(route.path)
        
        print("Expected paths:")
        for path in expected_paths:
            print(f"   {path}")
        
        print("\nActual paths:")
        for path in actual_paths:
            print(f"   {path}")
        
        # Check if expected paths exist
        missing_paths = []
        for expected in expected_paths:
            if expected not in actual_paths:
                missing_paths.append(expected)
        
        if missing_paths:
            print(f"\n❌ Missing paths: {missing_paths}")
            return False
        else:
            print("\n✅ All expected paths found")
            return True
            
    except Exception as e:
        print(f"❌ Route path test failed: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Admin Route Diagnostic Tool")
    print("=" * 50)
    
    success1 = test_admin_import()
    success2 = test_main_app() 
    success3 = test_route_paths()
    
    print("\n" + "=" * 50)
    if success1 and success2 and success3:
        print("✅ All tests passed - Admin routes should be working")
    else:
        print("❌ Some tests failed - Check the errors above")
    
    print("\n💡 If tests pass but /admin still returns 404:")
    print("   - Check if deployment has been updated")
    print("   - Clear browser cache")
    print("   - Check server logs for import errors")
