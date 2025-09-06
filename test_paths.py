#!/usr/bin/env python3
"""
Quick CoolCode Path Tester
Test the specific paths we discovered
"""

import requests

def test_specific_paths():
    """Test the specific paths we found"""
    
    base_url = "https://coolcode-hacker-34c5455cd908.herokuapp.com"
    
    print("🔥 CoolCode Path Tester 🔥")
    print("=" * 40)
    print(f"Base URL: {base_url}")
    print("=" * 40)
    
    # Paths to test based on discovery
    paths = [
        "/",                    # Root (confirmed working)
        "/instruction/",        # Found in HTML
        "/login",              # Common login path
        "/auth",               # Common auth path
        "/signin",             # Alternative login
        "/dashboard",          # Common dashboard
        "/student",            # Student interface
        "/assignments",        # Assignments page
        "/api/",               # API root
        "/api/coolcodehackteam/CX8de3ce71-3cbTY"  # Registration endpoint
    ]
    
    for path in paths:
        url = base_url + path
        try:
            response = requests.get(url, timeout=10)
            
            status = response.status_code
            content_type = response.headers.get('content-type', '')
            size = len(response.text)
            
            # Color coding
            if status == 200:
                status_icon = "✅"
            elif status in [301, 302]:
                status_icon = "🔄"
            elif status == 401:
                status_icon = "🔒"
            elif status == 403:
                status_icon = "🚫"
            elif status == 404:
                status_icon = "❌"
            else:
                status_icon = "❓"
            
            print(f"{status_icon} {path:<25} | {status} | {content_type:<20} | {size:>6} bytes")
            
            # Show content preview for interesting responses
            if status == 200 and size > 0:
                content_preview = response.text[:200].replace('\n', ' ').strip()
                if any(keyword in content_preview.lower() for keyword in ['login', 'username', 'password', 'assignment', 'coolcode', 'instruction']):
                    print(f"   📄 Preview: {content_preview}...")
                    
            # Check for redirects
            if status in [301, 302]:
                location = response.headers.get('location', '')
                if location:
                    print(f"   🔄 Redirects to: {location}")
            
        except requests.exceptions.Timeout:
            print(f"⏰ {path:<25} | TIMEOUT")
        except Exception as e:
            print(f"💥 {path:<25} | ERROR: {str(e)[:50]}")
    
    print("\n" + "=" * 40)
    print("💡 INSTRUCTIONS:")
    print("1. Open your browser and go to the root URL:")
    print(f"   {base_url}")
    print("2. Look for login forms, navigation, or instruction links")
    print("3. If you see content, look for ways to authenticate")
    print("4. Check browser dev tools for additional API calls")
    print("=" * 40)

if __name__ == "__main__":
    test_specific_paths()
