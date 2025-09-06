#!/usr/bin/env python3
"""
CoolCode UI Discovery Tool
Find the correct UI endpoint and explore the application structure
"""

import requests
import re
from urllib.parse import urljoin, urlparse
import time

class CoolCodeExplorer:
    def __init__(self):
        self.base_url = "https://coolcode-hacker-34c5455cd908.herokuapp.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        })
        
    def log(self, message, level="INFO"):
        colors = {
            "INFO": "\033[94m",
            "SUCCESS": "\033[92m", 
            "WARNING": "\033[93m",
            "ERROR": "\033[91m",
            "FOUND": "\033[95m",
            "RESET": "\033[0m"
        }
        color = colors.get(level, colors["INFO"])
        reset = colors["RESET"]
        timestamp = time.strftime("%H:%M:%S")
        print(f"{color}[{timestamp}] {level}: {message}{reset}")

    def test_endpoint(self, endpoint):
        """Test a single endpoint and return status info"""
        try:
            url = urljoin(self.base_url, endpoint)
            response = self.session.get(url, timeout=10)
            
            return {
                'url': url,
                'status': response.status_code,
                'content_type': response.headers.get('content-type', ''),
                'content': response.text[:500] if response.text else '',
                'size': len(response.text) if response.text else 0
            }
        except Exception as e:
            return {
                'url': urljoin(self.base_url, endpoint),
                'error': str(e)
            }

    def discover_ui_endpoints(self):
        """Try to find the correct UI endpoint"""
        self.log("🔍 Discovering UI endpoints...", "INFO")
        
        # Common UI endpoint patterns
        ui_candidates = [
            "/",
            "/ui",
            "/ui/",
            "/web",
            "/web/",
            "/app",
            "/app/",
            "/dashboard",
            "/dashboard/",
            "/login",
            "/login/",
            "/signin",
            "/signin/",
            "/auth",
            "/auth/",
            "/home",
            "/home/",
            "/index.html",
            "/main",
            "/main/",
            "/portal",
            "/portal/",
            "/student",
            "/student/",
            "/coolcode",
            "/coolcode/",
            "/education",
            "/education/"
        ]
        
        accessible_endpoints = []
        
        for endpoint in ui_candidates:
            result = self.test_endpoint(endpoint)
            
            if 'error' not in result:
                status = result['status']
                content_type = result['content_type']
                size = result['size']
                
                if status == 200:
                    self.log(f"✅ {endpoint} - {status} ({content_type}) [{size} bytes]", "SUCCESS")
                    accessible_endpoints.append(result)
                    
                    # Check if this looks like a UI
                    if any(keyword in result['content'].lower() for keyword in ['html', 'login', 'username', 'password', 'assignment', 'coolcode']):
                        self.log(f"🎯 {endpoint} - Looks like UI content!", "FOUND")
                        
                elif status == 302 or status == 301:
                    self.log(f"🔄 {endpoint} - {status} (Redirect)", "WARNING")
                    accessible_endpoints.append(result)
                elif status == 401:
                    self.log(f"🔒 {endpoint} - {status} (Auth required)", "WARNING")
                    accessible_endpoints.append(result)
                elif status == 403:
                    self.log(f"🚫 {endpoint} - {status} (Forbidden)", "WARNING")
                    accessible_endpoints.append(result)
                elif status != 404:
                    self.log(f"❓ {endpoint} - {status}", "INFO")
            else:
                self.log(f"💥 {endpoint} - {result['error']}", "ERROR")
        
        return accessible_endpoints

    def analyze_root_page(self):
        """Analyze the root page for clues"""
        self.log("📋 Analyzing root page...", "INFO")
        
        result = self.test_endpoint("/")
        
        if 'error' not in result and result['status'] == 200:
            content = result['content']
            
            # Look for links to other pages
            links = re.findall(r'href=["\']([^"\']+)["\']', content, re.IGNORECASE)
            if links:
                self.log(f"🔗 Found {len(links)} links in root page", "INFO")
                for link in links[:10]:  # Show first 10 links
                    if not link.startswith('http') and not link.startswith('#'):
                        self.log(f"   - {link}", "INFO")
            
            # Look for API endpoints mentioned
            api_refs = re.findall(r'/api/[^\s\'"<>]+', content, re.IGNORECASE)
            if api_refs:
                self.log(f"🔌 Found API references: {api_refs}", "FOUND")
            
            # Look for keywords
            keywords = ['login', 'username', 'password', 'assignment', 'coolcode', 'student', 'mentor']
            found_keywords = [kw for kw in keywords if kw.lower() in content.lower()]
            if found_keywords:
                self.log(f"🔑 Found keywords: {found_keywords}", "FOUND")
            
            # Show content preview
            self.log("📄 Root page content preview:", "INFO")
            print(content[:1000] + "..." if len(content) > 1000 else content)
            
        return result

    def discover_api_endpoints(self):
        """Discover API endpoints"""
        self.log("🔌 Discovering API endpoints...", "INFO")
        
        api_candidates = [
            "/api",
            "/api/",
            "/api/health",
            "/api/status",
            "/api/version",
            "/api/info",
            "/api/docs",
            "/api/swagger",
            "/api/openapi.json",
            "/api/v1",
            "/api/v1/",
            "/api/auth",
            "/api/auth/",
            "/api/login",
            "/api/users",
            "/api/user",
            "/api/assignments",
            "/api/assignment",
            "/api/scores",
            "/api/score",
            "/api/coolcodehackteam",
            "/api/coolcodehackteam/",
            "/api/api",
            "/api/api/",
            "/api/api/assignment",
            "/api/api/assignment/score"
        ]
        
        api_endpoints = []
        
        for endpoint in api_candidates:
            result = self.test_endpoint(endpoint)
            
            if 'error' not in result:
                status = result['status']
                
                if status in [200, 401, 403]:
                    self.log(f"✅ {endpoint} - {status}", "SUCCESS")
                    api_endpoints.append(result)
                    
                    if status == 200 and result['content']:
                        # Show API content preview
                        content_preview = result['content'][:200]
                        self.log(f"   Content: {content_preview}", "INFO")
                elif status != 404:
                    self.log(f"❓ {endpoint} - {status}", "INFO")
        
        return api_endpoints

    def test_registration_endpoint(self, username="CX8de3ce71-3cbTY"):
        """Test the challenge registration endpoint"""
        self.log("📝 Testing challenge registration endpoint...", "INFO")
        
        reg_endpoint = f"/api/coolcodehackteam/{username}"
        result = self.test_endpoint(reg_endpoint)
        
        if 'error' not in result:
            self.log(f"Registration endpoint: {result['status']}", "INFO")
            if result['content']:
                self.log(f"Response: {result['content']}", "INFO")
        
        return result

    def look_for_alternative_access(self):
        """Look for alternative ways to access the system"""
        self.log("🕵️ Looking for alternative access methods...", "INFO")
        
        # Check common file extensions
        file_candidates = [
            "/index.html",
            "/index.php",
            "/default.html",
            "/home.html",
            "/login.html",
            "/signin.html",
            "/app.html",
            "/main.html"
        ]
        
        for candidate in file_candidates:
            result = self.test_endpoint(candidate)
            if 'error' not in result and result['status'] == 200:
                self.log(f"📄 Found file: {candidate}", "FOUND")
        
        # Check for subdirectories
        subdirs = [
            "/public",
            "/static",
            "/assets",
            "/client",
            "/frontend",
            "/www"
        ]
        
        for subdir in subdirs:
            result = self.test_endpoint(subdir)
            if 'error' not in result and result['status'] in [200, 301, 302]:
                self.log(f"📁 Found directory: {subdir}", "FOUND")

    def run_full_discovery(self):
        """Run complete discovery process"""
        self.log("🔥 Starting CoolCode UI Discovery", "FOUND")
        self.log("=" * 60, "INFO")
        
        # Test base URL first
        self.log(f"🌐 Base URL: {self.base_url}", "INFO")
        
        # Step 1: Analyze root page
        root_result = self.analyze_root_page()
        
        print("\n" + "=" * 60)
        
        # Step 2: Discover UI endpoints
        ui_endpoints = self.discover_ui_endpoints()
        
        print("\n" + "=" * 60)
        
        # Step 3: Discover API endpoints
        api_endpoints = self.discover_api_endpoints()
        
        print("\n" + "=" * 60)
        
        # Step 4: Test registration
        reg_result = self.test_registration_endpoint()
        
        print("\n" + "=" * 60)
        
        # Step 5: Look for alternatives
        self.look_for_alternative_access()
        
        print("\n" + "=" * 60)
        
        # Summary
        self.log("📊 DISCOVERY SUMMARY", "FOUND")
        self.log("=" * 30, "INFO")
        
        if ui_endpoints:
            self.log(f"✅ Found {len(ui_endpoints)} accessible UI-like endpoints:", "SUCCESS")
            for endpoint in ui_endpoints:
                if endpoint['status'] == 200:
                    self.log(f"   🌐 {endpoint['url']} ({endpoint['status']})", "SUCCESS")
        else:
            self.log("❌ No clear UI endpoints found", "ERROR")
        
        if api_endpoints:
            self.log(f"✅ Found {len(api_endpoints)} accessible API endpoints:", "SUCCESS")
            for endpoint in api_endpoints:
                self.log(f"   🔌 {endpoint['url']} ({endpoint['status']})", "SUCCESS")
        
        # Recommendations
        print("\n💡 RECOMMENDATIONS:")
        print("1. Try accessing the root URL directly in browser: https://coolcode-hacker-34c5455cd908.herokuapp.com")
        print("2. If root shows content, look for navigation links")
        print("3. Check browser dev tools for redirects or AJAX calls")
        print("4. The API endpoint /api/api/assignment/score definitely exists (we got 403)")
        print("5. Try the registration endpoint to see if it provides more info")

def main():
    print("🔥" * 25)
    print("   CoolCode UI Discovery Tool")
    print("🔥" * 25)
    print()
    
    explorer = CoolCodeExplorer()
    explorer.run_full_discovery()

if __name__ == "__main__":
    main()
