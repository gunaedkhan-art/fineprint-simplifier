# matcher.py - Pattern detection and scoring system

from collections import defaultdict
from core_patterns import RISK_PATTERNS, GOOD_PATTERNS
from preprocess_text import preprocess_text
import json
import os
import re

CUSTOM_FILE = "custom_patterns.json"
PENDING_FILE = "pending_patterns.json"

def load_custom_patterns():
    if os.path.exists(CUSTOM_FILE):
        with open(CUSTOM_FILE, "r") as f:
            return json.load(f)
    return {"risks": {}, "good_points": {}}

def load_pending_patterns():
    if os.path.exists(PENDING_FILE):
        with open(PENDING_FILE, "r") as f:
            return json.load(f)
    return {"risks": {}, "good_points": {}}

def save_pending_patterns(patterns):
    with open(PENDING_FILE, "w") as f:
        json.dump(patterns, f, indent=2)

def get_all_core_patterns():
    """
    Get all core patterns (from core_patterns.py and custom_patterns.json)
    This is what we use for detection - NOT pending_patterns.json
    """
    # Start with core patterns
    all_risk_patterns = dict(RISK_PATTERNS)
    all_good_patterns = dict(GOOD_PATTERNS)
    
    # Add custom patterns if they exist
    custom_patterns = load_custom_patterns()
    for category, phrases in custom_patterns.get("risks", {}).items():
        if category not in all_risk_patterns:
            all_risk_patterns[category] = []
        all_risk_patterns[category].extend(phrases)
    
    for category, phrases in custom_patterns.get("good_points", {}).items():
        if category not in all_good_patterns:
            all_good_patterns[category] = []
        all_good_patterns[category].extend(phrases)
    
    # Deduplicate patterns within each category
    for category in all_risk_patterns:
        all_risk_patterns[category] = list(dict.fromkeys(all_risk_patterns[category]))
    
    for category in all_good_patterns:
        all_good_patterns[category] = list(dict.fromkeys(all_good_patterns[category]))
    
    return all_risk_patterns, all_good_patterns

def find_regex_matches(text, patterns_with_scores):
    """
    Find regex pattern matches in text with scoring
    Returns list of matches with their positions and scores
    """
    matches = []
    text_lower = text.lower()
    
    for category, data in patterns_with_scores.items():
        # Handle both new format (dict with score/patterns) and legacy format (list)
        if isinstance(data, dict) and "patterns" in data:
            # New format with scores
            score = data.get("score", 1)
            patterns = data.get("patterns", [])
        else:
            # Legacy format (list of patterns)
            score = 3  # Default score for legacy patterns
            patterns = data if isinstance(data, list) else []
        
        for pattern in patterns:
            try:
                # Compile regex pattern (case insensitive)
                regex = re.compile(pattern, re.IGNORECASE)
                
                for match in regex.finditer(text):
                    matches.append({
                        "match": match.group(0),  # Original case
                        "pattern": pattern,
                        "category": category,
                        "score": score,
                        "position": {
                            "start": match.start(),
                            "end": match.end()
                        }
                    })
            except re.error as e:
                print(f"Invalid regex pattern '{pattern}': {e}")
                continue
    
    return matches

def find_exact_phrase_matches(text, phrases):
    """
    Find exact phrase matches in text (case-insensitive)
    Returns list of matches with their positions (no overlapping matches)
    """
    matches = []
    text_lower = text.lower()
    
    for phrase in phrases:
        phrase_lower = phrase.lower()
        start = 0
        while True:
            pos = text_lower.find(phrase_lower, start)
            if pos == -1:
                break
            matches.append({
                "match": text[pos:pos + len(phrase)],  # Original case
                "position": {
                    "start": pos,
                    "end": pos + len(phrase)
                }
            })
            start = pos + len(phrase)  # Continue searching from end of this match
    
    return matches

def find_risks_in_text(text_or_pages) -> dict:
    """
    Find risk patterns in text using ONLY core patterns (not pending patterns)
    Returns: dict with categories as keys and lists of matches as values
    """
    grouped_matches = defaultdict(list)
    core_risk_patterns, _ = get_all_core_patterns()

    if isinstance(text_or_pages, str):
        # Single text string
        text = preprocess_text(text_or_pages)
        
        # Check core patterns only (exact matching)
        for category, phrases in core_risk_patterns.items():
            matches = find_exact_phrase_matches(text, phrases)
            for match in matches:
                grouped_matches[category].append({
                    "match": match["match"],
                    "score": 3,  # Default score for core patterns
                    "page": 1,  # Default to page 1 for single text
                    "position": match["position"]
                })
    else:
        # List of pages
        for page in text_or_pages:
            page_number = page["page_number"]
            text = preprocess_text(page["text"])

            # Check core patterns only (exact matching)
            for category, phrases in core_risk_patterns.items():
                matches = find_exact_phrase_matches(text, phrases)
                for match in matches:
                    grouped_matches[category].append({
                        "match": match["match"],
                        "score": 3,  # Default score for core patterns
                        "page": page_number,
                        "position": match["position"]
                    })

    # Keep all distinct occurrences but remove exact duplicates
    deduplicated_matches = {}
    for category, matches in grouped_matches.items():
        if matches:
            # Remove exact duplicates (same text, same position) but keep different occurrences
            seen_matches = set()
            unique_matches = []
            for match in matches:
                # Create a key based on match text and position to identify exact duplicates
                match_key = (match["match"].lower(), match["position"]["start"], match["position"]["end"])
                if match_key not in seen_matches:
                    seen_matches.add(match_key)
                    unique_matches.append(match)
            deduplicated_matches[category] = unique_matches

    return deduplicated_matches


def find_good_points_in_text(text_or_pages) -> dict:
    """
    Find good point patterns in text using ONLY core patterns (not pending patterns)
    Returns: dict with categories as keys and lists of matches as values
    """
    grouped_matches = defaultdict(list)
    _, core_good_patterns = get_all_core_patterns()

    if isinstance(text_or_pages, str):
        # Single text string
        text = preprocess_text(text_or_pages)
        
        # Check core patterns only (exact matching)
        for category, phrases in core_good_patterns.items():
            matches = find_exact_phrase_matches(text, phrases)
            for match in matches:
                grouped_matches[category].append({
                    "match": match["match"],
                    "score": 3,  # Default score for core patterns
                    "page": 1,  # Default to page 1 for single text
                    "position": match["position"]
                })
    else:
        # List of pages
        for page in text_or_pages:
            page_number = page["page_number"]
            text = preprocess_text(page["text"])

            # Check core patterns only (exact matching)
            for category, phrases in core_good_patterns.items():
                matches = find_exact_phrase_matches(text, phrases)
                for match in matches:
                    grouped_matches[category].append({
                        "match": match["match"],
                        "score": 3,  # Default score for core patterns
                        "page": page_number,
                        "position": match["position"]
                    })

    # Keep all distinct occurrences but remove exact duplicates
    deduplicated_matches = {}
    for category, matches in grouped_matches.items():
        if matches:
            # Remove exact duplicates (same text, same position) but keep different occurrences
            seen_matches = set()
            unique_matches = []
            for match in matches:
                # Create a key based on match text and position to identify exact duplicates
                match_key = (match["match"].lower(), match["position"]["start"], match["position"]["end"])
                if match_key not in seen_matches:
                    seen_matches.add(match_key)
                    unique_matches.append(match)
            deduplicated_matches[category] = unique_matches

    return deduplicated_matches


def detect_new_patterns(text_or_pages, existing_matches):
    """
    Detect new patterns that aren't in core patterns and store them in pending_patterns.json
    This function looks for potential patterns that weren't caught by exact matching
    """
    if isinstance(text_or_pages, str):
        text = text_or_pages
    else:
        text = " ".join([page["text"] for page in text_or_pages])
    
    # Simple heuristic to find potential patterns
    # Look for sentences that contain key words but weren't matched exactly
    potential_patterns = []
    
    # Key words that might indicate risks or benefits
    risk_keywords = ["fee", "charge", "penalty", "terminate", "cancel", "waive", "liability", "damage", "cost", "payment"]
    benefit_keywords = ["guarantee", "refund", "secure", "protect", "free", "no charge", "capped", "limit"]
    
    sentences = text.split('.')
    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) < 20 or len(sentence) > 200:  # Skip very short or very long sentences
            continue
            
        # Check if sentence contains key words
        sentence_lower = sentence.lower()
        has_risk_words = any(word in sentence_lower for word in risk_keywords)
        has_benefit_words = any(word in sentence_lower for word in benefit_keywords)
        
        # Check if this sentence wasn't already matched
        already_matched = False
        for category_matches in existing_matches.values():
            for match in category_matches:
                if sentence in match.get("match", "") or match.get("match", "") in sentence:
                    already_matched = True
                    break
            if already_matched:
                break
        
        if not already_matched:
            if has_risk_words:
                potential_patterns.append({
                    "type": "risk",
                    "category": "potential_risk",
                    "phrase": sentence
                })
            elif has_benefit_words:
                potential_patterns.append({
                    "type": "good_point", 
                    "category": "potential_benefit",
                    "phrase": sentence
                })
    
    # Store new patterns in pending_patterns.json
    if potential_patterns:
        pending = load_pending_patterns()
        custom_patterns = load_custom_patterns()
        
        for pattern in potential_patterns:
            pattern_type = pattern["type"]
            category = pattern["category"]
            phrase = pattern["phrase"]
            
            # Convert to backend format
            backend_category = "risks" if pattern_type == "risk" else "good_points"
            
            # Check if already exists in pending patterns
            already_in_pending = False
            for existing_category, data in pending.get(backend_category, {}).items():
                if isinstance(data, dict) and "patterns" in data:
                    if phrase in data["patterns"]:
                        already_in_pending = True
                        break
                elif isinstance(data, list):
                    if phrase in data:
                        already_in_pending = True
                        break
            
            # Check if already exists in active patterns (custom_patterns.json)
            already_in_custom = False
            for existing_category, phrases in custom_patterns.get(backend_category, {}).items():
                if phrase in phrases:
                    already_in_custom = True
                    break
            
            # Check if already exists in core patterns
            already_in_core = False
            if backend_category == "risks":
                for existing_category, phrases in RISK_PATTERNS.items():
                    if phrase in phrases:
                        already_in_core = True
                        break
            else:  # good_points
                for existing_category, phrases in GOOD_PATTERNS.items():
                    if phrase in phrases:
                        already_in_core = True
                        break
            
            # Only add if not already in any active patterns
            if not already_in_pending and not already_in_custom and not already_in_core:
                # Add to pending patterns
                if backend_category not in pending:
                    pending[backend_category] = {}
                
                if category not in pending[backend_category]:
                    pending[backend_category][category] = {
                        "score": 3,  # Default score
                        "patterns": []
                    }
                
                pending[backend_category][category]["patterns"].append(phrase)
        
        save_pending_patterns(pending)
    
    return potential_patterns

def score_contract(risks: dict, good_points: dict) -> dict:
    """
    Returns a dict with a qualitative rating and numeric score out of 10.
    Now considers severity scores for more nuanced evaluation.
    """
    # Calculate weighted scores
    risk_score = 0
    risk_count = 0
    for category, matches in risks.items():
        for match in matches:
            score = match.get("score", 3)  # Default to 3 if no score
            risk_score += score
            risk_count += 1
    
    benefit_score = 0
    benefit_count = 0
    for category, matches in good_points.items():
        for match in matches:
            score = match.get("score", 3)  # Default to 3 if no score
            benefit_score += score
            benefit_count += 1
    
    total_items = risk_count + benefit_count
    if total_items == 0:
        rating = "Neutral"
        score = 5
        risk_level = "None"
        benefit_level = "None"
    else:
        # Calculate average scores
        avg_risk = risk_score / risk_count if risk_count > 0 else 0
        avg_benefit = benefit_score / benefit_count if benefit_count > 0 else 0
        
        # Calculate overall score (0-10 scale)
        # Higher benefit scores improve the rating, higher risk scores worsen it
        base_score = 5  # Neutral starting point
        benefit_contribution = (avg_benefit / 5) * 3  # Max +3 points
        risk_penalty = (avg_risk / 5) * 3  # Max -3 points
        
        score = max(0, min(10, base_score + benefit_contribution - risk_penalty))
        score = round(score, 1)
        
        # Determine rating
        if score >= 8:
            rating = "Very Favorable"
        elif score >= 6:
            rating = "Favorable"
        elif score >= 4:
            rating = "Neutral"
        elif score >= 2:
            rating = "Risky"
        else:
            rating = "Very Risky"
        
        # Determine risk and benefit levels
        if avg_risk >= 4:
            risk_level = "High"
        elif avg_risk >= 2.5:
            risk_level = "Medium"
        else:
            risk_level = "Low"
            
        if avg_benefit >= 4:
            benefit_level = "High"
        elif avg_benefit >= 2.5:
            benefit_level = "Medium"
        else:
            benefit_level = "Low"

    return {
        "rating": rating,
        "score_out_of_10": score,
        "risk_level": risk_level,
        "benefit_level": benefit_level,
        "risk_count": risk_count,
        "benefit_count": benefit_count,
        "total_risk_score": risk_score,
        "total_benefit_score": benefit_score
    }