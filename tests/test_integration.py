# Integration tests for the IoT Device Status API
# Tests complete HTTP request/response flow with database

import pytest
import requests
import sqlite3
import os
import sys
import threading
import time
from multiprocessing import Process

# Add parent directory to path so we can import from app.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestAPIIntegration:
    # Integration tests for the complete API workflow
    
    BASE_URL = 'http://localhost:8000'
    API_KEY = 'dev-key-123'  # Default API key
    
    @property
    def headers(self):
        # Headers with API key for authenticated requests
        return {'X-API-Key': self.API_KEY}
    
    def setup_method(self):
        # Clean main database before each test to ensure isolation
        # Clear the main database that Flask is using
        conn = sqlite3.connect('device_status.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM device_status')
        conn.commit()
        conn.close()
        
        # Wait a moment to ensure database operation completes
        import time
        time.sleep(0.1)
    
    def test_server_health(self):
        # Test that the server is running and healthy
        response = requests.get(f'{self.BASE_URL}/health')
        assert response.status_code == 200
        
        data = response.json()
        assert data['status'] == 'healthy'
        assert 'message' in data
    
    def test_post_status_valid_data(self):
        # Test POST /status with valid device data
        device_data = {
            "device_id": "integration-test-001",
            "timestamp": "2025-06-19T14:00:00Z",
            "battery_level": 85,
            "rssi": -55,
            "online": True
        }
        
        response = requests.post(f'{self.BASE_URL}/status', json=device_data, headers=self.headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data['message'] == 'Status updated successfully'
    
    def test_post_then_get_device(self):
        # Test complete workflow: POST device data then GET it back
        # Step 1: POST device data
        device_data = {
            "device_id": "integration-test-002",
            "timestamp": "2025-06-19T15:30:00Z",
            "battery_level": 67,
            "rssi": -62,
            "online": False
        }
        
        post_response = requests.post(f'{self.BASE_URL}/status', json=device_data, headers=self.headers)
        assert post_response.status_code == 200
        
        # Step 2: GET the same device data back
        get_response = requests.get(f'{self.BASE_URL}/status/integration-test-002', headers=self.headers)
        assert get_response.status_code == 200
        
        retrieved_data = get_response.json()
        assert retrieved_data['device_id'] == device_data['device_id']
        assert retrieved_data['timestamp'] == device_data['timestamp']
        assert retrieved_data['battery_level'] == device_data['battery_level']
        assert retrieved_data['rssi'] == device_data['rssi']
        assert retrieved_data['online'] == device_data['online']
    
    def test_post_update_existing_device(self):
        # Test updating existing device data
        device_id = "integration-test-003"
        
        # Step 1: POST initial device data
        initial_data = {
            "device_id": device_id,
            "timestamp": "2025-06-19T10:00:00Z",
            "battery_level": 90,
            "rssi": -50,
            "online": True
        }
        
        response1 = requests.post(f'{self.BASE_URL}/status', json=initial_data, headers=self.headers)
        assert response1.status_code == 200
        
        # Step 2: POST updated data for same device
        updated_data = {
            "device_id": device_id,
            "timestamp": "2025-06-19T11:00:00Z",
            "battery_level": 75,  # Battery decreased
            "rssi": -60,  # Signal weakened
            "online": True
        }
        
        response2 = requests.post(f'{self.BASE_URL}/status', json=updated_data, headers=self.headers)
        assert response2.status_code == 200
        
        # Step 3: GET device data - should have updated values
        get_response = requests.get(f'{self.BASE_URL}/status/{device_id}', headers=self.headers)
        assert get_response.status_code == 200
        
        retrieved_data = get_response.json()
        assert retrieved_data['battery_level'] == 75  # Updated value
        assert retrieved_data['rssi'] == -60  # Updated value
        assert retrieved_data['timestamp'] == "2025-06-19T11:00:00Z"  # Updated timestamp
    
    def test_get_nonexistent_device(self):
        # Test GET for device that doesn't exist
        response = requests.get(f'{self.BASE_URL}/status/nonexistent-device', headers=self.headers)
        assert response.status_code == 404
        
        data = response.json()
        assert data['error'] == 'Device not found'
    
    def test_post_invalid_data(self):
        # Test POST with various invalid data scenarios
        # Missing required field
        invalid_data = {
            "device_id": "invalid-test-001",
            "timestamp": "2025-06-19T14:00:00Z",
            "battery_level": 85,
            # Missing rssi and online
        }
        
        response = requests.post(f'{self.BASE_URL}/status', json=invalid_data, headers=self.headers)
        assert response.status_code == 400
        assert 'Missing required field' in response.json()['error']
        
        # Invalid battery level
        invalid_data = {
            "device_id": "invalid-test-002",
            "timestamp": "2025-06-19T14:00:00Z",
            "battery_level": 150,  # Invalid range
            "rssi": -60,
            "online": True
        }
        
        response = requests.post(f'{self.BASE_URL}/status', json=invalid_data, headers=self.headers)
        assert response.status_code == 400
        assert 'battery_level must be an integer between 0 and 100' in response.json()['error']
    
    def test_authentication_missing_api_key(self):
        # Test requests without API key should fail
        device_data = {
            "device_id": "auth-test-001",
            "timestamp": "2025-06-19T14:00:00Z",
            "battery_level": 85,
            "rssi": -55,
            "online": True
        }
        
        # POST without API key
        response = requests.post(f'{self.BASE_URL}/status', json=device_data)
        assert response.status_code == 401
        assert 'Missing API key header' in response.json()['error']
        
        # GET without API key
        response = requests.get(f'{self.BASE_URL}/status/some-device')
        assert response.status_code == 401
        assert 'Missing API key header' in response.json()['error']
        
        # Summary without API key
        response = requests.get(f'{self.BASE_URL}/status/summary')
        assert response.status_code == 401
        assert 'Missing API key header' in response.json()['error']
    
    def test_authentication_invalid_api_key(self):
        # Test requests with invalid API key should fail
        invalid_headers = {'X-API-Key': 'invalid-key-999'}
        
        device_data = {
            "device_id": "auth-test-002",
            "timestamp": "2025-06-19T14:00:00Z",
            "battery_level": 85,
            "rssi": -55,
            "online": True
        }
        
        # POST with invalid API key
        response = requests.post(f'{self.BASE_URL}/status', json=device_data, headers=invalid_headers)
        assert response.status_code == 401
        assert 'Invalid API key' in response.json()['error']
        
        # GET with invalid API key
        response = requests.get(f'{self.BASE_URL}/status/some-device', headers=invalid_headers)
        assert response.status_code == 401
        assert 'Invalid API key' in response.json()['error']
        
        # Summary with invalid API key
        response = requests.get(f'{self.BASE_URL}/status/summary', headers=invalid_headers)
        assert response.status_code == 401
        assert 'Invalid API key' in response.json()['error']
    
    def test_summary_structure_with_known_data(self):
        # Test GET /status/summary returns proper structure (regardless of existing data)
        # Add a known device
        test_device = {
            "device_id": "structure-test-device",
            "timestamp": "2025-06-19T12:00:00Z",
            "battery_level": 88,
            "rssi": -52,
            "online": True
        }
        
        post_response = requests.post(f'{self.BASE_URL}/status', json=test_device, headers=self.headers)
        assert post_response.status_code == 200
        
        # GET summary
        response = requests.get(f'{self.BASE_URL}/status/summary', headers=self.headers)
        assert response.status_code == 200
        
        data = response.json()
        assert 'devices' in data
        assert isinstance(data['devices'], list)
        assert len(data['devices']) >= 1  # At least our test device
        
        # Find our test device in the results
        test_device_found = False
        for device in data['devices']:
            if device['device_id'] == 'structure-test-device':
                assert device['battery_level'] == 88
                assert device['online'] == True
                assert device['last_update'] == "2025-06-19T12:00:00Z"
                assert 'device_id' in device
                assert 'battery_level' in device
                assert 'online' in device
                assert 'last_update' in device
                test_device_found = True
                break
        
        assert test_device_found, "Test device not found in summary"
    
    def test_summary_multiple_specific_devices(self):
        # Test GET /status/summary with multiple specific devices we add
        # Use unique device IDs that won't conflict
        unique_prefix = "multi-test"
        devices = [
            {
                "device_id": f"{unique_prefix}-001",
                "timestamp": "2025-06-19T10:00:00Z",
                "battery_level": 90,
                "rssi": -50,
                "online": True
            },
            {
                "device_id": f"{unique_prefix}-002",
                "timestamp": "2025-06-19T10:30:00Z",
                "battery_level": 45,
                "rssi": -70,
                "online": False
            },
            {
                "device_id": f"{unique_prefix}-003",
                "timestamp": "2025-06-19T11:00:00Z",
                "battery_level": 78,
                "rssi": -55,
                "online": True
            }
        ]
        
        # POST all devices
        for device in devices:
            response = requests.post(f'{self.BASE_URL}/status', json=device, headers=self.headers)
            assert response.status_code == 200
        
        # GET summary
        response = requests.get(f'{self.BASE_URL}/status/summary', headers=self.headers)
        assert response.status_code == 200
        
        data = response.json()
        assert 'devices' in data
        
        # Find our specific devices in the results
        our_devices = [d for d in data['devices'] if d['device_id'].startswith(unique_prefix)]
        assert len(our_devices) == 3
        
        # Check that devices are ordered by device_id
        our_device_ids = [device['device_id'] for device in our_devices]
        assert our_device_ids == sorted(our_device_ids)
        
        # Check that summary contains expected fields and values
        for device in our_devices:
            assert 'device_id' in device
            assert 'battery_level' in device
            assert 'online' in device
            assert 'last_update' in device
            
            # Verify specific values match what we posted
            original = next(d for d in devices if d['device_id'] == device['device_id'])
            assert device['battery_level'] == original['battery_level']
            assert device['online'] == original['online']
            assert device['last_update'] == original['timestamp']
    
    def test_workflow_with_unique_devices(self):
        # Test complete workflow with multiple operations using unique device IDs
        # Use unique prefix to avoid conflicts with other tests
        unique_prefix = "workflow-unique"
        
        # 1. POST multiple devices
        devices = [
            {
                "device_id": f"{unique_prefix}-001",
                "timestamp": "2025-06-19T09:00:00Z",
                "battery_level": 100,
                "rssi": -45,
                "online": True
            },
            {
                "device_id": f"{unique_prefix}-002",
                "timestamp": "2025-06-19T09:15:00Z",
                "battery_level": 85,
                "rssi": -55,
                "online": True
            }
        ]
        
        for device in devices:
            response = requests.post(f'{self.BASE_URL}/status', json=device, headers=self.headers)
            assert response.status_code == 200
        
        # 2. GET individual devices
        for device in devices:
            response = requests.get(f'{self.BASE_URL}/status/{device["device_id"]}', headers=self.headers)
            assert response.status_code == 200
            data = response.json()
            assert data['device_id'] == device['device_id']
            assert data['battery_level'] == device['battery_level']
        
        # 3. GET summary and check our devices are there
        response = requests.get(f'{self.BASE_URL}/status/summary', headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        
        # Find our specific devices
        our_devices = [d for d in data['devices'] if d['device_id'].startswith(unique_prefix)]
        assert len(our_devices) == 2
        
        # 4. Update one device
        updated_device = {
            "device_id": f"{unique_prefix}-001",
            "timestamp": "2025-06-19T10:00:00Z",
            "battery_level": 90,  # Battery decreased
            "rssi": -50,
            "online": True
        }
        
        response = requests.post(f'{self.BASE_URL}/status', json=updated_device, headers=self.headers)
        assert response.status_code == 200
        
        # 5. Verify update in summary
        response = requests.get(f'{self.BASE_URL}/status/summary', headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        
        # Find the updated device in summary
        updated_device_summary = next(
            (d for d in data['devices'] if d['device_id'] == f'{unique_prefix}-001'), 
            None
        )
        assert updated_device_summary is not None
        assert updated_device_summary['battery_level'] == 90
        assert updated_device_summary['last_update'] == "2025-06-19T10:00:00Z"


# Note: These tests require the Flask server to be running on port 8000
# To run these tests:
# 1. Start the server: python app.py
# 2. In another terminal: pytest tests/test_integration.py -v