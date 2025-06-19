#!/usr/bin/env python3

# Test script for GET /status/{device_id} endpoint
# Run this after starting the Flask app and having some data from POST tests


import requests

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

def add_test_device():
    # Add a test device to make sure we have data
    print("\n1. Adding test device data")
    
    test_data = {
        "device_id": "sensor-get-test-123",
        "timestamp": "2025-06-19T10:30:00Z",
        "battery_level": 85,
        "rssi": -55,
        "online": True
    }
    
    response = requests.post(f'{BASE_URL}/status', json=test_data)
    print(f"POST Status Code: {response.status_code}")
    print(f"POST Response: {response.json()}")
    
    if response.status_code == 200:
        print("Test device added successfully")
        return True
    else:
        print("Failed to add test device")
        return False

def test_get_existing_device():
    # Test GET /status/{device_id} for existing device
    print("\n2. Testing GET /status/sensor-get-test-123")
    
    response = requests.get(f'{BASE_URL}/status/sensor-get-test-123')
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200:
        data = response.json()
        expected_fields = ['device_id', 'timestamp', 'battery_level', 'rssi', 'online']
        
        # Check all expected fields are present
        missing_fields = [field for field in expected_fields if field not in data]
        if missing_fields:
            print(f"Missing fields: {missing_fields}")
            return False
        
        # Check data matches what we posted
        if (data['device_id'] == 'sensor-get-test-123' and 
            data['battery_level'] == 85 and 
            data['rssi'] == -55 and 
            data['online'] == True):
            print("GET existing device working correctly")
            return True
        else:
            print("Data doesn't match expected values")
            return False
    else:
        print("GET existing device failed")
        return False

def test_get_nonexistent_device():
    # Test GET /status/{device_id} for device that doesn't exist
    print("\n3. Testing GET /status/nonexistent-device")
    
    response = requests.get(f'{BASE_URL}/status/nonexistent-device')
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 404:
        print("GET nonexistent device handling working correctly")
        return True
    else:
        print("GET nonexistent device handling failed")
        return False

def test_get_from_previous_post_tests():
    # Test GET for device from previous POST tests
    print("\n4. Testing GET /status/sensor-abc-123 (from previous POST tests)")
    
    response = requests.get(f'{BASE_URL}/status/sensor-abc-123')
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200:
        print("Can retrieve device from previous POST tests")
        return True
    elif response.status_code == 404:
        print("Device from previous POST tests not found (maybe database was reset)")
        return False
    else:
        print("Unexpected error retrieving previous device")
        return False

if __name__ == '__main__':
    print("Testing GET /status/{device_id} endpoint")
    print("=" * 50)
    
    # Check if server is running
    if not test_health():
        print("\nStart the server first with: python app.py")
        exit(1)
    
    # Run tests
    success_count = 0
    total_tests = 4
    
    if add_test_device():
        success_count += 1
    
    if test_get_existing_device():
        success_count += 1
        
    if test_get_nonexistent_device():
        success_count += 1
        
    if test_get_from_previous_post_tests():
        success_count += 1
    
    print("\n" + "=" * 50)
    print(f"GET endpoint testing completed!")
    print(f"Tests passed: {success_count}/{total_tests}")
    
    if success_count == total_tests:
        print("All tests passed! GET endpoint is working correctly.")
    else:
        print("Some tests failed. Check the output above.")