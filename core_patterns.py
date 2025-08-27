# core_patterns.py - Consolidated pattern definitions
# This file contains all the core patterns used for detection

# Risk patterns - specific phrases to detect
RISK_PATTERNS = {
    "early_termination_fee": [
        "early termination fee",
        "early termination fees", 
        "cancellation fee",
        "cancellation fees",
        "termination penalty",
        "termination penalties",
        "termination charge",
        "termination charges",
        "penalty for early termination",
        "penalties for early termination",
    ],
    
    "automatic_renewal": [
        "automatically renew",
        "automatic renewal",
        "subscription renewal",
        "renewal term",
        "renewal terms",
        "continuous service",
        "auto-bill",
        "auto-billed",
        "auto-billing",
    ],
    
    "arbitration_clause": [
        "binding arbitration",
        "final decision by arbitrator",
        "dispute resolution via arbitration",
        "waive your right to sue",
        "waive the right to sue",
        "waives your right to sue",
        "waived your right to sue",
        "arbitration proceedings",
    ],
    
    "late_payment_penalties": [
        "late payment fee",
        "late payment fees",
        "late charge",
        "late charges",
        "overdue payment penalty",
        "overdue payment penalties",
        "overdue payment charge",
        "overdue payment charges",
        "interest on overdue",
        "charged if payment is late",
        "finance charge",
        "finance charges",
    ],
    
    "non_refundable": [
        "non-refundable",
        "non refundable",
        "no refund",
        "no refunds",
        "not entitled to a refund",
        "non-returnable",
        "cannot be returned",
    ],
    
    "limited_liability": [
        "limited liability",
        "limited responsibility",
        "not liable for",
        "no liability for",
        "held harmless",
        "indemnify",
        "indemnification",
        "not responsible for",
    ],
    
    "service_availability_disclaimer": [
        "availability not guaranteed",
        "availability may vary",
        "subject to change without notice",
        "service may be unavailable",
        "services may be unavailable",
        "no guarantee of availability",
    ],
    
    "unilateral_modification": [
        "reserve the right to change",
        "reserves the right to change",
        "may modify these terms",
        "subject to change at any discretion",
        "subject to change at our discretion",
    ],
    
    "hidden_charges": [
        "additional charges may apply",
        "extra fees not included",
        "hidden costs may be incurred",
        "surcharges apply",
        "administrative fees additional",
        "processing fees extra",
        "service charges not included",
        "handling fees additional cost",
    ],
    
    "data_sharing": [
        "consent to share personal data",
        "authorize sharing personal information",
        "permission to share sensitive data",
        "data may be shared with third parties",
        "information disclosed to partners",
        "consent to third party access",
    ],
    
    "rights_limitation": [
        "waive right to appeal",
        "no right to appeal",
        "final decision no appeal",
        "binding decision no recourse",
        "limited right to challenge",
    ]
}

# Good point patterns - specific phrases to detect
GOOD_PATTERNS = {
    "grace_period": [
        "grace period of 14 days",
        "grace period of 30 days",
        "grace period of 60 days",
        "grace period of 90 days",
        "no penalty within 14 days",
        "no penalty within 30 days",
        "no penalty within 60 days",
        "no penalty within 90 days",
    ],
    
    "money_back_guarantee": [
        "money-back guarantee",
        "money back guarantee",
        "refund guarantee",
    ],
    
    "data_protection": [
        "data will be kept secure",
        "data is kept secure",
        "data will be kept confidential",
        "data is kept confidential",
        "GDPR compliant",
    ],
    
    "limitation_of_liability": [
        "limit of liability",
        "cap of liability",
        "cap on liability",
        "liability limited to",
    ],
    
    "no_win_no_fee": [
        "no win no fee",
        "no win no fee arrangement",
        "no win no fee agreement",
        "no win no fee basis",
    ],
    
    "fee_caps": [
        "success fee capped at 25%",
        "maximum success fee 25%",
        "success fee not exceeding 25%",
        "success fee limited to 25%",
    ],
    
    "cost_protection": [
        "no charge for work after offer deadline",
        "no additional charge work after offer",
        "no fee work done after offer",
    ],
    
    "cooling_off": [
        "14-day cooling-off period",
        "14 day cooling off period",
        "cooling-off period 14 days",
        "cancellation period 14 days",
    ],
    
    "transparency": [
        "clear explanation of charges",
        "transparent fee structure",
        "clear fee breakdown",
        "detailed cost explanation",
    ]
}
