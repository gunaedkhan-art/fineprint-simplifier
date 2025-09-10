#!/usr/bin/env python3
"""
Test script for admin pattern approval functionality
"""

import json
import os
from matcher import load_pending_patterns, save_pending_patterns, load_custom_patterns

def test_pending_patterns():
    print("🧪 Testing Admin Pattern Approval")
    print("=" * 40)
    
    # Test loading pending patterns
    try:
        pending = load_pending_patterns()
        print(f"✅ Loaded pending patterns: {len(pending)} categories")
        
        # Show structure
        if pending:
            for ptype in ["risks", "good_points"]:
                if ptype in pending:
                    print(f"  {ptype}: {len(pending[ptype])} categories")
                    for category, data in pending[ptype].items():
                        if isinstance(data, dict) and "patterns" in data:
                            print(f"    {category}: {len(data['patterns'])} patterns")
                        elif isinstance(data, list):
                            print(f"    {category}: {len(data)} patterns")
        else:
            print("  No pending patterns found")
            
    except Exception as e:
        print(f"❌ Error loading pending patterns: {e}")
    
    # Test loading custom patterns
    try:
        custom = load_custom_patterns()
        print(f"✅ Loaded custom patterns: {len(custom)} types")
        
        for ptype, categories in custom.items():
            print(f"  {ptype}: {len(categories)} categories")
            
    except Exception as e:
        print(f"❌ Error loading custom patterns: {e}")
    
    # Test file permissions
    try:
        test_data = {"test": "data"}
        with open("test_patterns.json", "w") as f:
            json.dump(test_data, f, indent=2)
        
        with open("test_patterns.json", "r") as f:
            loaded = json.load(f)
        
        os.remove("test_patterns.json")
        print("✅ File read/write permissions working")
        
    except Exception as e:
        print(f"❌ File permission error: {e}")

def create_test_pending_pattern():
    """Create a test pending pattern for testing"""
    print("\n🔧 Creating test pending pattern...")
    
    test_pattern = {
        "risks": {
            "test_category": {
                "patterns": ["This is a test pattern for approval testing"]
            }
        },
        "good_points": {}
    }
    
    try:
        save_pending_patterns(test_pattern)
        print("✅ Test pending pattern created")
        print("   You can now test the admin approval functionality")
        print("   Pattern: 'This is a test pattern for approval testing'")
        print("   Category: 'test_category'")
        print("   Type: 'risks'")
        
    except Exception as e:
        print(f"❌ Error creating test pattern: {e}")

if __name__ == "__main__":
    test_pending_patterns()
    create_test_pending_pattern()
