# pricing_config.py - Freemium pricing configuration

# Free tier limits
FREE_TIER_LIMITS = {
    "documents_per_month": 3,
    "features": [
        "plain_english_summary",
        "basic_risk_detection",
        "basic_good_points_detection"
    ]
}

# Paid tier features
PAID_TIER_FEATURES = [
    "unlimited_documents",
    "risk_score_badges",
    "side_by_side_comparison", 
    "export_pdf",
    "export_word",
    "export_excel",
    "advanced_analytics",
    "priority_support",
    "saved_analyses"
]

# Feature descriptions for UI
FEATURE_DESCRIPTIONS = {
    "plain_english_summary": "Clear, easy-to-understand summary of document terms",
    "basic_risk_detection": "Identify potential risks in legal documents",
    "basic_good_points_detection": "Find favorable terms and benefits",
    "unlimited_documents": "Upload as many documents as you need",
    "risk_score_badges": "Color-coded risk assessment (Green/Yellow/Red)",
    "side_by_side_comparison": "Compare two documents side-by-side",
    "export_pdf": "Export analysis results to PDF format",
    "export_word": "Export analysis results to Word document",
    "export_excel": "Export analysis results to Excel spreadsheet",
    "advanced_analytics": "Detailed contract scoring and insights",
    "priority_support": "Priority customer support",
    "saved_analyses": "Save up to 50 analysis results with custom names and notes"
}

# Pricing information
PRICING = {
    "monthly": 9.99,
    "yearly": 99.99,  # ~17% discount
    "currency": "USD"
}
