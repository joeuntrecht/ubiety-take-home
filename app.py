import sqlite3
import os
from datetime import datetime
from functools import wraps
from flask import Flask, request, jsonify

app = Flask(__name__)

# Database setup
DATABASE = 'device_status.db'

# API Key configuration
VALID_API_KEYS = os.getenv('API_KEYS', 'dev-key-123,test-key-456').split(',')

def require_api_key(f):
    # Decorator to require API key authentication
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return jsonify({'error': 'Missing API key header (X-API-Key)'}), 401
        if api_key not in VALID_API_KEYS:
            return jsonify({'error': 'Invalid API key'}), 401
        return f(*args, **kwargs)
    return decorated

def init_db():
    # Init the database with device_status table
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS device_status (
            device_id TEXT PRIMARY KEY,
            timestamp TEXT NOT NULL,
            battery_level INTEGER NOT NULL,
            rssi INTEGER NOT NULL,
            online BOOLEAN NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()

def validate_device_data(data):
    # Validate device data - returns (is_valid, error_message)
    if data is None:
        return False, 'No JSON data provided'
    
    # Check required fields
    required_fields = ['device_id', 'timestamp', 'battery_level', 'rssi', 'online']
    for field in required_fields:
        if field not in data:
            return False, f'Missing required field: {field}'
    
    # Validate battery level
    if not isinstance(data['battery_level'], int) or not (0 <= data['battery_level'] <= 100):
        return False, 'battery_level must be an integer between 0 and 100'
    
    # Validate RSSI
    if not isinstance(data['rssi'], int):
        return False, 'rssi must be an integer'
    
    # Validate online status
    if not isinstance(data['online'], bool):
        return False, 'online must be a boolean'
    
    # Validate timestamp format
    try:
        datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
    except ValueError:
        return False, 'timestamp must be in ISO 8601 format'
    
    return True, None

def format_device_response(row):
    # Convert SQLite row to device response format
    return {
        'device_id': row['device_id'],
        'timestamp': row['timestamp'],
        'battery_level': row['battery_level'],
        'rssi': row['rssi'],
        'online': bool(row['online'])
    }

def format_summary_device(row):
    # Convert SQLite row to summary device format
    return {
        'device_id': row['device_id'],
        'battery_level': row['battery_level'],
        'online': bool(row['online']),
        'last_update': row['timestamp']
    }

@app.route('/status', methods=['POST'])
@require_api_key
def submit_status():
    # Accept device status update
    try:
        data = request.get_json()
        
        # Validate data using helper function
        is_valid, error_message = validate_device_data(data)
        if not is_valid:
            return jsonify({'error': error_message}), 400
        
        # Store in database (upsert - insert or update if device_id exists)
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO device_status 
            (device_id, timestamp, battery_level, rssi, online, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            data['device_id'],
            data['timestamp'],
            data['battery_level'],
            data['rssi'],
            data['online'],
            datetime.utcnow().isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Status updated successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/status/<device_id>', methods=['GET'])
@require_api_key
def get_device_status(device_id):
    # Get the last known status for a specific device
    try:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row  # This enables column access by name
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT device_id, timestamp, battery_level, rssi, online 
            FROM device_status 
            WHERE device_id = ?
        ''', (device_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row is None:
            return jsonify({'error': 'Device not found'}), 404
        
        # Convert row to dictionary using helper function
        device_status = format_device_response(row)
        
        return jsonify(device_status), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/status/summary', methods=['GET'])
@require_api_key
def get_status_summary():
    # Get summary of all devices with their most recent status
    try:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row  # This enables column access by name
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT device_id, battery_level, online, timestamp 
            FROM device_status 
            ORDER BY device_id
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        # Build summary list using helper function
        summary = [format_summary_device(row) for row in rows]
        
        return jsonify({'devices': summary}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    # Basic health check endpoint - no authentication required
    return jsonify({'status': 'healthy', 'message': 'API is running'}), 200

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=8000, debug=True)