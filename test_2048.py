"""
Test script for 2048 game server
"""
import requests
import json

def test_2048_endpoint():
    """Test the 2048 game endpoint locally"""
    
    base_url = "http://localhost:10000"
    
    # Test data
    test_payload = {
        "grid": [
            [2, 2, None, None],
            [4, 4, None, None],
            [None, None, None, None],
            [None, None, None, None]
        ],
        "mergeDirection": "LEFT"
    }
    
    try:
        response = requests.post(f"{base_url}/2048", json=test_payload)
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            data = response.json()
            if "nextGrid" in data and "endGame" in data:
                print("✅ 2048 endpoint working correctly!")
                return True
            else:
                print("❌ Invalid response format")
                return False
        else:
            print("❌ Non-200 status code")
            return False
            
    except Exception as e:
        print(f"❌ Error testing endpoint: {e}")
        return False

if __name__ == "__main__":
    test_2048_endpoint()
