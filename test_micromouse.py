#!/usr/bin/env python3
"""
Test script for micromouse controller
"""

import requests
import json
import time

def test_micromouse():
    """Test the micromouse endpoint"""
    base_url = "http://localhost:8080"
    
    # Test data
    game_uuid = "test-game-123"
    
    # Test 1: Start new game
    print("Test 1: Starting new game...")
    payload = {
        "game_uuid": game_uuid,
        "sensor_data": [0, 0, 0, 0, 0],
        "total_time_ms": 0,
        "goal_reached": False,
        "run_time_ms": 0,
        "run": 0,
        "momentum": 0
    }
    
    try:
        response = requests.post(f"{base_url}/micro-mouse", json=payload)
        print(f"Response status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✓ New game started successfully")
        else:
            print("✗ Failed to start new game")
            return
            
    except Exception as e:
        print(f"✗ Error starting new game: {e}")
        return
    
    # Test 2: Get debug info
    print("\nTest 2: Getting debug info...")
    try:
        response = requests.get(f"{base_url}/micro-mouse/debug/{game_uuid}")
        print(f"Debug response status: {response.status_code}")
        print(f"Debug response: {response.json()}")
        
        if response.status_code == 200:
            print("✓ Debug info retrieved successfully")
        else:
            print("✗ Failed to get debug info")
            
    except Exception as e:
        print(f"✗ Error getting debug info: {e}")
    
    # Test 3: Update game state
    print("\nTest 3: Updating game state...")
    update_payload = {
        "game_uuid": game_uuid,
        "sensor_data": [1, 0, 0, 0, 1],  # Walls on left and right
        "total_time_ms": 1000,
        "run_time_ms": 1000,
        "momentum": 1
    }
    
    try:
        response = requests.post(f"{base_url}/micro-mouse", json=update_payload)
        print(f"Update response status: {response.status_code}")
        print(f"Update response: {response.json()}")
        
        if response.status_code == 200:
            print("✓ Game state updated successfully")
        else:
            print("✗ Failed to update game state")
            
    except Exception as e:
        print(f"✗ Error updating game state: {e}")
    
    # Test 4: Get stats
    print("\nTest 4: Getting game stats...")
    try:
        response = requests.get(f"{base_url}/micro-mouse/stats/{game_uuid}")
        print(f"Stats response status: {response.status_code}")
        print(f"Stats response: {response.json()}")
        
        if response.status_code == 200:
            print("✓ Game stats retrieved successfully")
        else:
            print("✗ Failed to get game stats")
            
    except Exception as e:
        print(f"✗ Error getting game stats: {e}")

if __name__ == "__main__":
    print("Testing micromouse controller...")
    test_micromouse()
    print("\nTest completed!")
