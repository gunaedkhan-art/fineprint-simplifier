#!/usr/bin/env python3
import requests
import json

def test_frontend_simulation():
    """Simulate the frontend behavior to see what should be displayed"""
    
    # Test the analyze endpoint
    url = "http://localhost:8000/analyze"
    test_file = "test_contract.pdf"
    
    with open(test_file, 'rb') as f:
        files = {'file': (test_file, f, 'application/pdf')}
        data = {'user_id': 'test123'}
        
        response = requests.post(url, files=files, data=data)
        
        if response.status_code == 200:
            result = response.json()
            
            print("=== FRONTEND SIMULATION ===")
            print(f"Response received: {result}")
            
            # Simulate the frontend logic
            if result.get('is_visitor'):
                print("\n--- VISITOR FLOW ---")
                summary = result.get('visitor_summary', {})
                print(f"Should display visitor summary with:")
                print(f"  - Risk count: {summary.get('risk_count', 0)}")
                print(f"  - Good point count: {summary.get('good_point_count', 0)}")
                print(f"  - Quality: {summary.get('quality_assessment', 'unknown')}")
                print(f"  - Total pages: {summary.get('total_pages', 0)}")
                
                # Check if the numbers are reasonable
                risk_count = summary.get('risk_count', 0)
                good_count = summary.get('good_point_count', 0)
                
                if risk_count > 0 or good_count > 0:
                    print(f"\n✅ PATTERN RECOGNITION WORKING: Found {risk_count} risks and {good_count} good points")
                else:
                    print(f"\n❌ PATTERN RECOGNITION ISSUE: No patterns found")
            else:
                print("\n--- LOGGED IN USER FLOW ---")
                analysis = result.get('analysis', {})
                print(f"Should display full analysis: {analysis}")
        else:
            print(f"Error: {response.status_code} - {response.text}")

if __name__ == "__main__":
    test_frontend_simulation()
