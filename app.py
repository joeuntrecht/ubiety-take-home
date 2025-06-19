import sqlite3
from datetime import datetime
from flask import Flask, request, jsonify

app = Flask(__name__)

# Database setup
DATABASE = 'device_status.db'

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

@app.route('/status', methods=['POST'])
def submit_status():
    # Accept device status update
    try:
        data = request.get_json()
        
        # Check if we got JSON data
        if data is None:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        # Basic validation - check required fields
        required_fields = ['device_id', 'timestamp', 'battery_level', 'rssi', 'online']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Validate data types and ranges
        if not isinstance(data['battery_level'], int) or not (0 <= data['battery_level'] <= 100):
            return jsonify({'error': 'battery_level must be an integer between 0 and 100'}), 400
        
        if not isinstance(data['rssi'], int):
            return jsonify({'error': 'rssi must be an integer'}), 400
        
        if not isinstance(data['online'], bool):
            return jsonify({'error': 'online must be a boolean'}), 400
        
        # Validate timestamp format (basic check)
        try:
            datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
        except ValueError:
            return jsonify({'error': 'timestamp must be in ISO 8601 format'}), 400
        
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
        
        # Convert row to dictionary
        device_status = {
            'device_id': row['device_id'],
            'timestamp': row['timestamp'],
            'battery_level': row['battery_level'],
            'rssi': row['rssi'],
            'online': bool(row['online'])
        }
        
        return jsonify(device_status), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    # Basic health check endpoint
    return jsonify({'status': 'healthy', 'message': 'API is running'}), 200

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=8000)