# analyzer.py

from pdf_parser import extract_text_from_pdf
from matcher import find_risks_in_text, find_good_points_in_text, score_contract, detect_new_patterns

def analyze_pdf(file_path: str) -> dict:
    """
    Extracts text from a PDF, finds risks/good points overall and per page.
    Returns a dict with matches and page-level data for highlighting.
    """
    pdf_extraction = extract_text_from_pdf(file_path)  # dict with pages, quality_assessment, etc.
    pages = pdf_extraction.get("pages", [])
    if not pages:
        return {"success": False, "error": "Unable to extract text"}

    # Full text for overall scoring
    full_text = " ".join(p["text"] for p in pages)

    # Overall matches using core patterns only
    risks_overall = find_risks_in_text(full_text)
    goods_overall = find_good_points_in_text(full_text)

    # Detect new potential patterns and store in pending_patterns.json
    all_existing_matches = {**risks_overall, **goods_overall}
    new_patterns = detect_new_patterns(full_text, all_existing_matches)

    # Calculate contract rating
    contract_rating = score_contract(risks_overall, goods_overall)

    # Per-page matches for highlighting
    page_matches = []
    for page in pages:
        page_text = page["text"]
        page_matches.append({
            "page_number": page["page_number"],
            "text": page_text,
            "risks": find_risks_in_text(page_text),
            "good_points": find_good_points_in_text(page_text)
        })

    return {
        "success": True,
        "risks": risks_overall,
        "good_points": goods_overall,
        "contract_rating": contract_rating,
        "total_matches": sum(len(v) for v in risks_overall.values()) +
                         sum(len(v) for v in goods_overall.values()),
        "pages": page_matches
    }