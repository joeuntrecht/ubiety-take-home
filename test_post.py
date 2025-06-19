#!/usr/bin/env python3

# Simple test script to test just the POST /status endpoint
# Run this after starting the Flask app with: python app.py

import requests
import json

BASE_URL = 'http://localhost:8000'

def test_health():
    # Test that the server is running
    print("Testing server health...")
    try:
        response = requests.get(f'{BASE_URL}/health')
        print(f"Server is running: {response.json()}")
        return True
    except Exception as e:
        print(f"Server not running: {e}")
        return False

def test_valid_post():
    # Test POST /status with valid data
    print("\n1. Testing POST /status with valid data...")
    
    test_data = {
        "device_id": "sensor-abc-123",
        "timestamp": "2025-06-09T14:00:00Z",
        "battery_level": 76,
        "rssi": -60,
        "online": True
    }
    
    response = requests.post(f'{BASE_URL}/status', json=test_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200:
        print("Valid POST successful")
    else:
        print("Valid POST failed")

def test_missing_field():
    # Test POST /status with missing field
    print("\n2. Testing POST /status with missing field...")
    
    test_data = {
        "device_id": "sensor-abc-123",
        "timestamp": "2025-06-09T14:00:00Z",
        "battery_level": 76,
        # Missing rssi and online
    }
    
    response = requests.post(f'{BASE_URL}/status', json=test_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 400:
        print("Missing field validation working")
    else:
        print("Missing field validation failed")

def test_invalid_battery():
    # Test POST /status with invalid battery level
    print("\n3. Testing POST /status with invalid battery level...")
    
    test_data = {
        "device_id": "sensor-abc-123",
        "timestamp": "2025-06-09T14:00:00Z",
        "battery_level": 150,  # Invalid - over 100
        "rssi": -60,
        "online": True
    }
    
    response = requests.post(f'{BASE_URL}/status', json=test_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 400:
        print("Battery validation working")
    else:
        print("Battery validation failed")

def test_update_existing():
    # Test updating an existing device
    print("\n4. Testing POST /status to update existing device...")
    
    test_data = {
        "device_id": "sensor-abc-123",  # Same device as test 1
        "timestamp": "2025-06-09T15:00:00Z",  # Different time
        "battery_level": 65,  # Different battery
        "rssi": -65,
        "online": False  # Different status
    }
    
    response = requests.post(f'{BASE_URL}/status', json=test_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200:
        print("Device update successful")
    else:
        print("Device update failed")

if __name__ == '__main__':
    print("Testing POST /status endpoint")
    
    # Check if server is running
    if not test_health():
        print("\nStart the server first with: python app.py")
        exit(1)
    
    # Run POST tests
    test_valid_post()
    test_missing_field()
    test_invalid_battery()
    test_update_existing()
    
    print("POST endpoint testing completed!")
    print("\nNext step: Check if device_status.db file was created in your directory")