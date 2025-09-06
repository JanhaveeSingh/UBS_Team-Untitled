#!/usr/bin/env python3
"""
Let's decode the ACCESS_TOKEN to understand its structure
"""

import base64
import json

def decode_token():
    token = "eyJ1c2VybmFtZSI6IkNYOGRlM2NlNzEtM2NiVFkiLCJoYXNoIjoiMDZiNzRiNTQ5ZDUwNzVhMTRmMjFiY2FmODU1Mzg0OGE4N2U4NjczODMxMzI1ZGJkMmQ2ODgzODM4NDAwNTI5MCJ9"
    
    try:
        # Add padding if needed
        missing_padding = len(token) % 4
        if missing_padding:
            token += '=' * (4 - missing_padding)
        
        # Decode from base64
        decoded_bytes = base64.b64decode(token)
        decoded_str = decoded_bytes.decode('utf-8')
        
        print("Raw decoded string:")
        print(decoded_str)
        print()
        
        # Try to parse as JSON
        try:
            data = json.loads(decoded_str)
            print("Parsed JSON:")
            print(json.dumps(data, indent=2))
            
            # Extract the username from the token
            if 'username' in data:
                actual_username = data['username']
                print(f"\nActual username in token: {actual_username}")
                return actual_username
        except json.JSONDecodeError:
            print("Not valid JSON")
            
    except Exception as e:
        print(f"Error decoding token: {e}")
        
    return None

if __name__ == "__main__":
    print("🔍 Decoding ACCESS_TOKEN...")
    print("="*50)
    
    username = decode_token()
    
    if username:
        print(f"\n💡 We should try using username: '{username}' instead of '98ixul'!")
