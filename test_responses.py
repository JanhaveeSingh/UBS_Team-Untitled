#!/usr/bin/env python3
"""
Test different response formats to see what the challenge server expects.
"""

import requests
import json
from flask import Flask, jsonify, request
import threading
import time

app = Flask(__name__)

# Different response formats to test
response_formats = [
    # Format 1: Simple username/password
    {"username": "UBS_Team-Untitled", "password": ""},
    
    # Format 2: Team info
    {"teamName": "UBS_Team-Untitled", "serverUrl": "http://127.0.0.1:5000"},
    
    # Format 3: Java-style naming
    {"teamName": "UBS_Team-Untitled", "password": "", "serverUrl": "http://127.0.0.1:5000"},
    
    # Format 4: Full team response
    {
        "id": 1,
        "teamName": "UBS_Team-Untitled", 
        "serverUrl": "http://127.0.0.1:5000",
        "status": "ACTIVE",
        "members": []
    },
    
    # Format 5: Registration response
    {
        "username": "UBS_Team-Untitled",
        "password": "",
        "teamName": "UBS_Team-Untitled",
        "serverUrl": "http://127.0.0.1:5000",
        "status": "REGISTERED"
    }
]

current_format = 0

@app.route('/', methods=['GET', 'POST'])
def root():
    return jsonify(response_formats[current_format])

@app.route('/api/coolcodehackteam/<username>', methods=['GET', 'POST'])
def register(username):
    # Always return the challenge server format we discovered
    return jsonify({"username": username, "password": ""})

@app.route('/test/<int:format_id>')
def test_format(format_id):
    global current_format
    if 0 <= format_id < len(response_formats):
        current_format = format_id
        return f"Switched to format {format_id}: {response_formats[format_id]}"
    return "Invalid format ID"

@app.route('/current')
def current():
    return jsonify(response_formats[current_format])

def run_server():
    app.run(host='127.0.0.1', port=5000, debug=False)

if __name__ == "__main__":
    print("🧪 Response Format Tester")
    print("=" * 50)
    
    # Start Flask server in background
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    time.sleep(2)  # Wait for server to start
    
    print("\nServer running on http://127.0.0.1:5000")
    print("\nAvailable endpoints:")
    print("- GET /             - Returns current format")
    print("- GET /test/<id>    - Switch to format <id>")
    print("- GET /current      - Show current format")
    print("- GET /api/coolcodehackteam/<name> - Registration endpoint")
    
    print(f"\nCurrent format ({current_format}):")
    print(json.dumps(response_formats[current_format], indent=2))
    
    print("\nAll available formats:")
    for i, fmt in enumerate(response_formats):
        print(f"Format {i}: {fmt}")
    
    print("\nTo test a format:")
    print("1. curl http://127.0.0.1:5000/test/<format_id>")
    print("2. curl http://127.0.0.1:5000/")
    print("3. Test with challenge server")
    
    # Keep the script running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")
