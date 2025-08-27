#!/usr/bin/env python3
"""
Test script to demonstrate the new scoring interface
"""

import json
from matcher import load_pending_patterns, save_pending_patterns

def test_scoring_interface():
    """Test the scoring interface functionality"""
    
    print("🧪 Testing Scoring Interface\n")
    
    # Test 1: Load current patterns
    print("📋 Test 1: Loading Current Patterns")
    patterns = load_pending_patterns()
    print(f"   Current patterns structure: {json.dumps(patterns, indent=2)}")
    print()
    
    # Test 2: Add a test pattern with scoring
    print("📋 Test 2: Adding Test Pattern with Score")
    test_pattern = {
        "risks": {
            "test_category": {
                "score": 4,
                "patterns": [
                    "\\btest\\b.*\\bpattern\\b.*\\bwith\\b.*\\bscore\\b"
                ]
            }
        }
    }
    
    # Merge with existing patterns
    for category, subcategories in test_pattern.items():
        if category not in patterns:
            patterns[category] = {}
        for subcategory, data in subcategories.items():
            patterns[category][subcategory] = data
    
    save_pending_patterns(patterns)
    print("   Added test pattern with score 4")
    print()
    
    # Test 3: Verify the pattern was saved
    print("📋 Test 3: Verifying Pattern Save")
    loaded_patterns = load_pending_patterns()
    if "test_category" in loaded_patterns.get("risks", {}):
        score = loaded_patterns["risks"]["test_category"]["score"]
        pattern_list = loaded_patterns["risks"]["test_category"]["patterns"]
        print(f"   Test pattern found with score: {score}")
        print(f"   Pattern: {pattern_list[0]}")
    else:
        print("   Test pattern not found")
    print()
    
    # Test 4: Simulate frontend pattern format
    print("📋 Test 4: Simulating Frontend Format")
    formatted_patterns = []
    
    for category, subcategories in loaded_patterns.items():
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
    
    print(f"   Formatted patterns: {json.dumps(formatted_patterns, indent=2)}")
    print()
    
    # Test 5: Clean up test pattern
    print("📋 Test 5: Cleaning Up Test Pattern")
    if "test_category" in loaded_patterns.get("risks", {}):
        del loaded_patterns["risks"]["test_category"]
        save_pending_patterns(loaded_patterns)
        print("   Test pattern removed")
    print()
    
    print("✅ Scoring interface tests completed!")

if __name__ == "__main__":
    test_scoring_interface()
