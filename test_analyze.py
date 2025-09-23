#!/usr/bin/env python3
import requests
import os

# Test the analyze endpoint
def test_analyze():
    url = "http://localhost:8000/analyze"
    
    # Check if test file exists
    test_file = "test_contract.pdf"
    if not os.path.exists(test_file):
        print(f"Test file {test_file} not found")
        return
    
    # Prepare the file upload
    with open(test_file, 'rb') as f:
        files = {'file': (test_file, f, 'application/pdf')}
        data = {'user_id': 'test123'}
        
        try:
            print("Sending request to analyze endpoint...")
            response = requests.post(url, files=files, data=data)
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            
            # Parse and display the response structure
            if response.status_code == 200:
                try:
                    result = response.json()
                    print(f"\nParsed Response Structure:")
                    print(f"- is_visitor: {result.get('is_visitor')}")
                    print(f"- visitor_summary: {result.get('visitor_summary')}")
                    if result.get('visitor_summary'):
                        summary = result['visitor_summary']
                        print(f"  - risk_count: {summary.get('risk_count')}")
                        print(f"  - good_point_count: {summary.get('good_point_count')}")
                        print(f"  - quality_assessment: {summary.get('quality_assessment')}")
                except Exception as e:
                    print(f"Error parsing JSON: {e}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_analyze()
