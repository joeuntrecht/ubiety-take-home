# Unit tests for device data validation functions

import pytest
import sys
import os

# Add parent directory to path so we can import from app.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import validate_device_data


class TestValidateDeviceData:
    # Test the validate_device_data function
    
    def test_valid_data(self):
        # Test validation with completely valid data
        valid_data = {
            "device_id": "sensor-abc-123",
            "timestamp": "2025-06-19T14:00:00Z",
            "battery_level": 76,
            "rssi": -60,
            "online": True
        }
        
        is_valid, error_message = validate_device_data(valid_data)
        assert is_valid == True
        assert error_message is None
    
    def test_none_data(self):
        # Test validation with None data
        is_valid, error_message = validate_device_data(None)
        assert is_valid == False
        assert error_message == "No JSON data provided"
    
    def test_missing_device_id(self):
        # Test validation with missing device_id
        data = {
            "timestamp": "2025-06-19T14:00:00Z",
            "battery_level": 76,
            "rssi": -60,
            "online": True
        }
        
        is_valid, error_message = validate_device_data(data)
        assert is_valid == False
        assert error_message == "Missing required field: device_id"
    
    def test_missing_timestamp(self):
        # Test validation with missing timestamp
        data = {
            "device_id": "sensor-abc-123",
            "battery_level": 76,
            "rssi": -60,
            "online": True
        }
        
        is_valid, error_message = validate_device_data(data)
        assert is_valid == False
        assert error_message == "Missing required field: timestamp"
    
    def test_missing_battery_level(self):
        # Test validation with missing battery_level
        data = {
            "device_id": "sensor-abc-123",
            "timestamp": "2025-06-19T14:00:00Z",
            "rssi": -60,
            "online": True
        }
        
        is_valid, error_message = validate_device_data(data)
        assert is_valid == False
        assert error_message == "Missing required field: battery_level"
    
    def test_missing_rssi(self):
        # Test validation with missing rssi
        data = {
            "device_id": "sensor-abc-123",
            "timestamp": "2025-06-19T14:00:00Z",
            "battery_level": 76,
            "online": True
        }
        
        is_valid, error_message = validate_device_data(data)
        assert is_valid == False
        assert error_message == "Missing required field: rssi"
    
    def test_missing_online(self):
        # Test validation with missing online
        data = {
            "device_id": "sensor-abc-123",
            "timestamp": "2025-06-19T14:00:00Z",
            "battery_level": 76,
            "rssi": -60
        }
        
        is_valid, error_message = validate_device_data(data)
        assert is_valid == False
        assert error_message == "Missing required field: online"
    
    def test_battery_level_too_high(self):
        # Test validation with battery level over 100
        data = {
            "device_id": "sensor-abc-123",
            "timestamp": "2025-06-19T14:00:00Z",
            "battery_level": 150,
            "rssi": -60,
            "online": True
        }
        
        is_valid, error_message = validate_device_data(data)
        assert is_valid == False
        assert error_message == "battery_level must be an integer between 0 and 100"
    
    def test_battery_level_negative(self):
        # Test validation with negative battery level
        data = {
            "device_id": "sensor-abc-123",
            "timestamp": "2025-06-19T14:00:00Z",
            "battery_level": -10,
            "rssi": -60,
            "online": True
        }
        
        is_valid, error_message = validate_device_data(data)
        assert is_valid == False
        assert error_message == "battery_level must be an integer between 0 and 100"
    
    def test_battery_level_not_integer(self):
        # Test validation with battery level as string
        data = {
            "device_id": "sensor-abc-123",
            "timestamp": "2025-06-19T14:00:00Z",
            "battery_level": "76",
            "rssi": -60,
            "online": True
        }
        
        is_valid, error_message = validate_device_data(data)
        assert is_valid == False
        assert error_message == "battery_level must be an integer between 0 and 100"
    
    def test_rssi_not_integer(self):
        # Test validation with RSSI as string
        data = {
            "device_id": "sensor-abc-123",
            "timestamp": "2025-06-19T14:00:00Z",
            "battery_level": 76,
            "rssi": "-60",
            "online": True
        }
        
        is_valid, error_message = validate_device_data(data)
        assert is_valid == False
        assert error_message == "rssi must be an integer"
    
    def test_online_not_boolean(self):
        # Test validation with online as string
        data = {
            "device_id": "sensor-abc-123",
            "timestamp": "2025-06-19T14:00:00Z",
            "battery_level": 76,
            "rssi": -60,
            "online": "true"
        }
        
        is_valid, error_message = validate_device_data(data)
        assert is_valid == False
        assert error_message == "online must be a boolean"
    
    def test_invalid_timestamp_format(self):
        # Test validation with invalid timestamp format
        data = {
            "device_id": "sensor-abc-123",
            "timestamp": "invalid-timestamp",
            "battery_level": 76,
            "rssi": -60,
            "online": True
        }
        
        is_valid, error_message = validate_device_data(data)
        assert is_valid == False
        assert error_message == "timestamp must be in ISO 8601 format"
    
    def test_boundary_values(self):
        # Test validation with boundary values
        # Test battery level = 0
        data = {
            "device_id": "sensor-abc-123",
            "timestamp": "2025-06-19T14:00:00Z",
            "battery_level": 0,
            "rssi": -60,
            "online": True
        }
        
        is_valid, error_message = validate_device_data(data)
        assert is_valid == True
        assert error_message is None
        
        # Test battery level = 100
        data["battery_level"] = 100
        is_valid, error_message = validate_device_data(data)
        assert is_valid == True
        assert error_message is None
    
    def test_different_timestamp_formats(self):
        # Test validation with different valid timestamp formats
        base_data = {
            "device_id": "sensor-abc-123",
            "battery_level": 76,
            "rssi": -60,
            "online": True
        }
        
        # Test Z format
        data = base_data.copy()
        data["timestamp"] = "2025-06-19T14:00:00Z"
        is_valid, error_message = validate_device_data(data)
        assert is_valid == True
        
        # Test +00:00 format
        data["timestamp"] = "2025-06-19T14:00:00+00:00"
        is_valid, error_message = validate_device_data(data)
        assert is_valid == True