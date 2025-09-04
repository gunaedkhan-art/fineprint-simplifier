# preprocess_text.py

import re

def preprocess_text(text: str) -> str:
    # Handle edge cases
    if not isinstance(text, str):
        return ""
    if not text:
        return ""
    
    # Remove extra whitespace, newlines, and lower the case
    text = re.sub(r'\s+', ' ', text)
    return text.lower()