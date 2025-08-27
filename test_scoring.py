#!/usr/bin/env python3
"""
Test script to demonstrate the new scoring system
"""

from matcher import find_risks_in_text, find_good_points_in_text, score_contract

def test_scoring_system():
    """Test various contract scenarios with the new scoring system"""
    
    print("🧪 Testing New Scoring System\n")
    
    # Test Case 1: High Risk Contract
    print("📋 Test Case 1: High Risk Contract")
    high_risk_text = """
    This agreement includes a success fee of 100% of basic charges.
    You must cancel within 14 days or owe costs.
    You consent to share personal sensitive data with third parties.
    You waive your right to appeal any decision.
    Additional charges may apply.
    """
    
    risks1 = find_risks_in_text(high_risk_text)
    goods1 = find_good_points_in_text(high_risk_text)
    score1 = score_contract(risks1, goods1)
    
    print(f"   Rating: {score1['rating']}")
    print(f"   Score: {score1['score_out_of_10']}/10")
    print(f"   Risk Level: {score1['risk_level']}")
    print(f"   Benefit Level: {score1['benefit_level']}")
    print(f"   Risk Count: {score1['risk_count']}")
    print(f"   Total Risk Score: {score1['total_risk_score']}")
    print()
    
    # Test Case 2: Balanced Contract
    print("📋 Test Case 2: Balanced Contract")
    balanced_text = """
    This is a no win no fee arrangement.
    Success fee is capped at 25% of damages.
    No charge for work done after the last date for accepting offer.
    You have a 14-day cooling-off period.
    Clear explanation of charges provided.
    """
    
    risks2 = find_risks_in_text(balanced_text)
    goods2 = find_good_points_in_text(balanced_text)
    score2 = score_contract(risks2, goods2)
    
    print(f"   Rating: {score2['rating']}")
    print(f"   Score: {score2['score_out_of_10']}/10")
    print(f"   Risk Level: {score2['risk_level']}")
    print(f"   Benefit Level: {score2['benefit_level']}")
    print(f"   Benefit Count: {score2['benefit_count']}")
    print(f"   Total Benefit Score: {score2['total_benefit_score']}")
    print()
    
    # Test Case 3: Very Favorable Contract
    print("📋 Test Case 3: Very Favorable Contract")
    favorable_text = """
    This is a no win no fee agreement with comprehensive service.
    Success fee is limited to 25% of damages.
    No charge for work after offer deadline.
    Appeals and enforcement actions included.
    Client retains control over proceedings.
    Option to opt out of disclosure.
    Check existing insurance before purchasing ATE.
    14-day cooling-off period applies.
    Transparent fee structure provided.
    """
    
    risks3 = find_risks_in_text(favorable_text)
    goods3 = find_good_points_in_text(favorable_text)
    score3 = score_contract(risks3, goods3)
    
    print(f"   Rating: {score3['rating']}")
    print(f"   Score: {score3['score_out_of_10']}/10")
    print(f"   Risk Level: {score3['risk_level']}")
    print(f"   Benefit Level: {score3['benefit_level']}")
    print(f"   Benefit Count: {score3['benefit_count']}")
    print(f"   Total Benefit Score: {score3['total_benefit_score']}")
    print()
    
    # Test Case 4: Low Risk, Low Benefit
    print("📋 Test Case 4: Low Risk, Low Benefit")
    low_impact_text = """
    Check existing insurance before purchasing ATE.
    Clear explanation of charges.
    """
    
    risks4 = find_risks_in_text(low_impact_text)
    goods4 = find_good_points_in_text(low_impact_text)
    score4 = score_contract(risks4, goods4)
    
    print(f"   Rating: {score4['rating']}")
    print(f"   Score: {score4['score_out_of_10']}/10")
    print(f"   Risk Level: {score4['risk_level']}")
    print(f"   Benefit Level: {score4['benefit_level']}")
    print(f"   Risk Count: {score4['risk_count']}")
    print(f"   Benefit Count: {score4['benefit_count']}")
    print()
    
    # Test Case 5: Empty Contract
    print("📋 Test Case 5: Empty Contract")
    empty_text = """
    This is a standard contract with no notable terms.
    """
    
    risks5 = find_risks_in_text(empty_text)
    goods5 = find_good_points_in_text(empty_text)
    score5 = score_contract(risks5, goods5)
    
    print(f"   Rating: {score5['rating']}")
    print(f"   Score: {score5['score_out_of_10']}/10")
    print(f"   Risk Level: {score5['risk_level']}")
    print(f"   Benefit Level: {score5['benefit_level']}")
    print()

if __name__ == "__main__":
    test_scoring_system()
