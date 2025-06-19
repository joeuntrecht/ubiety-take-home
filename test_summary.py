#!/usr/bin/env python3

# Test script for GET /status/summary endpoint

import requests

BASE_URL = 'http://localhost:8000'
API_KEY = 'dev-key-123'  # Default API key

def test_health():
    # Test that the server is running
    print("Testing server health")
    try:
        response = requests.get(f'{BASE_URL}/health')
        print(f"Server is running: {response.json()}")
        return True
    except Exception as e:
        print(f"Server not running: {e}")
        return False

def add_multiple_test_devices():
    # Add multiple test devices
    print("\n1. Adding multiple test devices")
    
    test_devices = [
        {
            "device_id": "sensor-kitchen-001",
            "timestamp": "2025-06-19T10:30:00Z",
            "battery_level": 85,
            "rssi": -55,
            "online": True
        },
        {
            "device_id": "sensor-bedroom-002",
            "timestamp": "2025-06-19T10:25:00Z",
            "battery_level": 42,
            "rssi": -72,
            "online": False
        },
        {
            "device_id": "sensor-garage-003",
            "timestamp": "2025-06-19T10:35:00Z",
            "battery_level": 95,
            "rssi": -48,
            "online": True
        }
    ]
    
    headers = {'X-API-Key': API_KEY}
    success_count = 0
    for device in test_devices:
        response = requests.post(f'{BASE_URL}/status', json=device, headers=headers)
        if response.status_code == 200:
            success_count += 1
            print(f"Added device: {device['device_id']}")
        else:
            print(f"Failed to add device: {device['device_id']}")
    
    print(f"Successfully added {success_count}/{len(test_devices)} devices")
    return success_count > 0

def test_summary_endpoint():
    # Test GET /status/summary endpoint
    print("\n2. Testing GET /status/summary")
    
    headers = {'X-API-Key': API_KEY}
    response = requests.get(f'{BASE_URL}/status/summary', headers=headers)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code != 200:
        print(f"Error Response: {response.json()}")
        return False
    
    data = response.json()
    print(f"Response: {data}")
    
    # Check response structure
    if 'devices' not in data:
        print("Missing 'devices' key in response")
        return False
    
    devices = data['devices']
    if not isinstance(devices, list):
        print("'devices' should be a list")
        return False
    
    print(f"Found {len(devices)} devices in summary")
    
    # Check each device has required fields
    required_fields = ['device_id', 'battery_level', 'online', 'last_update']
    for i, device in enumerate(devices):
        print(f"Device {i+1}: {device}")
        
        missing_fields = [field for field in required_fields if field not in device]
        if missing_fields:
            print(f"Device {i+1} missing fields: {missing_fields}")
            return False
        
        # Check data types
        if not isinstance(device['battery_level'], int):
            print(f"Device {i+1}: battery_level should be int")
            return False
        
        if not isinstance(device['online'], bool):
            print(f"Device {i+1}: online should be bool")
            return False
        
        if not isinstance(device['device_id'], str):
            print(f"Device {i+1}: device_id should be string")
            return False
        
        if not isinstance(device['last_update'], str):
            print(f"Device {i+1}: last_update should be string")
            return False
    
    print("Summary endpoint working correctly")
    return True

def test_summary_no_api_key():
    # Test GET /status/summary without API key
    print("\n3. Testing GET /status/summary without API key")
    
    response = requests.get(f'{BASE_URL}/status/summary')
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 401:
        print("Authentication working correctly")
        return True
    else:
        print("Authentication failed")
        return False

def test_summary_with_no_devices():
    # Test summary when no devices exist (requires clean database)
    print("\n4. Testing summary structure (even with existing devices)")
    
    headers = {'X-API-Key': API_KEY}
    response = requests.get(f'{BASE_URL}/status/summary', headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if 'devices' in data and isinstance(data['devices'], list):
            print("Summary returns correct structure")
            return True
        else:
            print("Summary structure is incorrect")
            return False
    else:
        print("Summary endpoint failed")
        return False

def test_summary_ordering():
    # Test that devices are returned in order by device_id
    print("\n5. Testing device ordering in summary")
    
    headers = {'X-API-Key': API_KEY}
    response = requests.get(f'{BASE_URL}/status/summary', headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        devices = data['devices']
        
        if len(devices) > 1:
            device_ids = [device['device_id'] for device in devices]
            sorted_ids = sorted(device_ids)
            
            if device_ids == sorted_ids:
                print("Devices are correctly ordered by device_id")
                return True
            else:
                print(f"Devices not ordered correctly: {device_ids} vs {sorted_ids}")
                return False
        else:
            print("Need multiple devices to test ordering, but structure looks correct")
            return True
    else:
        print("Summary endpoint failed")
        return False

if __name__ == '__main__':
    print("Testing GET /status/summary endpoint")
    print("=" * 50)
    
    # Check if server is running
    if not test_health():
        print("\nStart the server first with: python app.py")
        exit(1)
    
    # Run tests
    success_count = 0
    total_tests = 5
    
    if add_multiple_test_devices():
        success_count += 1
    
    if test_summary_endpoint():
        success_count += 1
    
    if test_summary_no_api_key():
        success_count += 1
        
    if test_summary_with_no_devices():
        success_count += 1
        
    if test_summary_ordering():
        success_count += 1
    
    print("\n" + "=" * 50)
    print(f"Summary endpoint testing completed!")
    print(f"Tests passed: {success_count}/{total_tests}")
    
    if success_count == total_tests:
        print("All tests passed! Summary endpoint is working correctly.")
    else:
        print("Some tests failed. Check the output above.")