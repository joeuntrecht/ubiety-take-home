# Unit tests for data formatting functions

import pytest
import sys
import os

# Add parent directory to path so we can import from app.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import format_device_response, format_summary_device


class MockRow:
    # Mock SQLite Row object for testing
    def __init__(self, **kwargs):
        self._data = kwargs
    
    def __getitem__(self, key):
        return self._data[key]


class TestFormatDeviceResponse:
    # Test the format_device_response function
    
    def test_format_device_response(self):
        # Test formatting a device response
        mock_row = MockRow(
            device_id="sensor-test-123",
            timestamp="2025-06-19T14:00:00Z",
            battery_level=85,
            rssi=-55,
            online=1  # SQLite stores boolean as integer
        )
        
        result = format_device_response(mock_row)
        
        expected = {
            'device_id': "sensor-test-123",
            'timestamp': "2025-06-19T14:00:00Z",
            'battery_level': 85,
            'rssi': -55,
            'online': True  # Should convert to boolean
        }
        
        assert result == expected
    
    def test_format_device_response_offline(self):
        # Test formatting a device response for offline device
        mock_row = MockRow(
            device_id="sensor-offline-456",
            timestamp="2025-06-19T13:00:00Z",
            battery_level=20,
            rssi=-80,
            online=0  # SQLite stores False as 0
        )
        
        result = format_device_response(mock_row)
        
        expected = {
            'device_id': "sensor-offline-456",
            'timestamp': "2025-06-19T13:00:00Z",
            'battery_level': 20,
            'rssi': -80,
            'online': False  # Should convert to boolean
        }
        
        assert result == expected
    
    def test_format_device_response_boundary_values(self):
        # Test formatting with boundary values
        mock_row = MockRow(
            device_id="sensor-boundary-789",
            timestamp="2025-06-19T12:00:00Z",
            battery_level=0,  # Minimum battery
            rssi=-100,  # Very weak signal
            online=1
        )
        
        result = format_device_response(mock_row)
        
        assert result['battery_level'] == 0
        assert result['rssi'] == -100
        assert result['online'] == True


class TestFormatSummaryDevice:
    # Test the format_summary_device function
    
    def test_format_summary_device(self):
        # Test formatting a summary device entry
        mock_row = MockRow(
            device_id="sensor-summary-123",
            battery_level=75,
            online=1,
            timestamp="2025-06-19T14:30:00Z"
        )
        
        result = format_summary_device(mock_row)
        
        expected = {
            'device_id': "sensor-summary-123",
            'battery_level': 75,
            'online': True,
            'last_update': "2025-06-19T14:30:00Z"
        }
        
        assert result == expected
    
    def test_format_summary_device_offline(self):
        # Test formatting a summary for offline device
        mock_row = MockRow(
            device_id="sensor-summary-offline",
            battery_level=15,
            online=0,  # Offline
            timestamp="2025-06-19T10:00:00Z"
        )
        
        result = format_summary_device(mock_row)
        
        expected = {
            'device_id': "sensor-summary-offline",
            'battery_level': 15,
            'online': False,
            'last_update': "2025-06-19T10:00:00Z"
        }
        
        assert result == expected
    
    def test_format_summary_device_full_battery(self):
        # Test formatting with full battery
        mock_row = MockRow(
            device_id="sensor-full-battery",
            battery_level=100,
            online=1,
            timestamp="2025-06-19T15:00:00Z"
        )
        
        result = format_summary_device(mock_row)
        
        assert result['battery_level'] == 100
        assert result['online'] == True
        assert result['last_update'] == "2025-06-19T15:00:00Z"
    
    def test_format_summary_device_empty_battery(self):
        # Test formatting with empty battery
        mock_row = MockRow(
            device_id="sensor-empty-battery",
            battery_level=0,
            online=0,  # Likely offline due to empty battery
            timestamp="2025-06-19T08:00:00Z"
        )
        
        result = format_summary_device(mock_row)
        
        assert result['battery_level'] == 0
        assert result['online'] == False