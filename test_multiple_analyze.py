#!/usr/bin/env python3
import requests
import os
import time

# Test the analyze endpoint multiple times
def test_multiple_analyze():
    url = "http://localhost:8000/analyze"
    test_file = "test_contract.pdf"
    
    if not os.path.exists(test_file):
        print(f"Test file {test_file} not found")
        return
    
    print("Testing pattern recognition consistency...")
    
    for i in range(5):
        print(f"\n--- Test {i+1} ---")
        
        with open(test_file, 'rb') as f:
            files = {'file': (test_file, f, 'application/pdf')}
            data = {'user_id': f'test{i+1}'}
            
            try:
                response = requests.post(url, files=files, data=data)
                print(f"Status Code: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"Risk count: {result.get('visitor_summary', {}).get('risk_count', 'N/A')}")
                    print(f"Good point count: {result.get('visitor_summary', {}).get('good_point_count', 'N/A')}")
                else:
                    print(f"Error: {response.text[:200]}...")
                    
            except Exception as e:
                print(f"Error: {e}")
        
        # Small delay between tests
        time.sleep(1)

if __name__ == "__main__":
    test_multiple_analyze()
