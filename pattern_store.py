import json
import os

CUSTOM_PATTERNS_FILE = "custom_patterns.json"
PENDING_PATTERNS_FILE = "pending_patterns.json"

def load_json_file(filepath, default=None):
    if not os.path.exists(filepath):
        return default or {}
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json_file(filepath, data):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def load_custom_patterns():
    return load_json_file(CUSTOM_PATTERNS_FILE, {"risks": {}, "good_points": {}})

def save_custom_patterns(patterns):
    save_json_file(CUSTOM_PATTERNS_FILE, patterns)

def load_pending_patterns():
    return load_json_file(PENDING_PATTERNS_FILE, {"risks": {}, "good_points": {}})

def save_pending_patterns(patterns):
    save_json_file(PENDING_PATTERNS_FILE, patterns)
