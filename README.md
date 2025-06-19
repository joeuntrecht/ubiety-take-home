# ubiety-take-home
Take-home assessment: IoT Device Status Service backend API

# IoT Device Status API

A Flask-based REST API for managing IoT device status data including battery levels, signal strength, and connectivity status.

## Features

- **POST /status** - Submit device status updates
- **GET /status/{device_id}** - Retrieve specific device status
- **GET /status/summary** - Get summary of all devices
- **GET /health** - Health check endpoint
- **API key authentication** - Secure endpoints with configurable API keys
- **Data validation** - Comprehensive input validation and error handling
- **SQLite database** - Persistent data storage with upsert functionality

## Quick Start

### Prerequisites
- Python 3.7+ OR Docker and Docker Compose
- pip (if running without Docker)

### Installation

#### Option 1: Docker (Recommended)
```bash
# Clone the repository
git clone <repository-url>
cd ubiety-take-home

# Start with Docker Compose
docker-compose up
```

The API will be available at `http://localhost:8000`

#### Option 2: Local Python
```bash
# Clone the repository
git clone <repository-url>
cd ubiety-take-home

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

The API will be available at `http://localhost:8000`

### Basic Usage

**Submit device status:**
```bash
curl -X POST http://localhost:8000/status \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-key-123" \
  -d '{
    "device_id": "sensor-001",
    "timestamp": "2025-06-19T14:00:00Z",
    "battery_level": 85,
    "rssi": -55,
    "online": true
  }'
```

**Get device status:**
```bash
curl -H "X-API-Key: dev-key-123" http://localhost:8000/status/sensor-001
```

**Get all devices summary:**
```bash
curl -H "X-API-Key: dev-key-123" http://localhost:8000/status/summary
```

**Health check (no authentication required):**
```bash
curl http://localhost:8000/health
```

## Authentication

All API endpoints except `/health` require authentication using an API key.

### API Key Header
Include the API key in the `X-API-Key` header:
```
X-API-Key: your-api-key-here
```

### Configuration
API keys are configured via the `API_KEYS` environment variable:
```bash
# Single API key
export API_KEYS="your-production-key"

# Multiple API keys (comma-separated)
export API_KEYS="key1,key2,key3"
```

**Default Keys** (for development):
- `dev-key-123`
- `test-key-456`

### Authentication Responses
- `401 Unauthorized` - Missing or invalid API key
- `200 OK` - Valid API key, request processed

## API Documentation

### POST /status
Submit device status update.

**Authentication:** Required

**Request Headers:**
```
Content-Type: application/json
X-API-Key: your-api-key
```

**Request Body:**
```json
{
  "device_id": "string (required)",
  "timestamp": "ISO 8601 timestamp (required)",
  "battery_level": "integer 0-100 (required)",
  "rssi": "integer (required)",
  "online": "boolean (required)"
}
```

**Response:**
- `200 OK` - Status updated successfully
- `400 Bad Request` - Invalid data or missing fields
- `401 Unauthorized` - Missing or invalid API key

### GET /status/{device_id}
Retrieve specific device status.

**Authentication:** Required

**Request Headers:**
```
X-API-Key: your-api-key
```

**Response:**
- `200 OK` - Returns device data
- `404 Not Found` - Device not found
- `401 Unauthorized` - Missing or invalid API key

### GET /status/summary
Get summary of all devices.

**Authentication:** Required

**Request Headers:**
```
X-API-Key: your-api-key
```

**Response:**
```json
{
  "devices": [
    {
      "device_id": "sensor-001",
      "battery_level": 85,
      "online": true,
      "last_update": "2025-06-19T14:00:00Z"
    }
  ]
}
```

**Response Codes:**
- `200 OK` - Returns devices array
- `401 Unauthorized` - Missing or invalid API key

### GET /health
Health check endpoint.

**Authentication:** Not required

**Response:**
```json
{
  "status": "healthy",
  "message": "API is running"
}
```

## Docker Development

### Running with Docker

**Start the application:**
```bash
docker compose up
```

**Start in background:**
```bash
docker compose up -d
```

**View logs:**
```bash
docker compose logs -f
```

**Stop the application:**
```bash
docker compose down
```

**Rebuild after code changes:**
```bash
# Force rebuild to pick up code changes
docker compose build --no-cache
docker compose up
```

### Running Tests with Docker

```bash
# Install test dependencies in container
docker compose exec api pip install pytest

# Run unit tests
docker compose exec api pytest tests/test_validation.py tests/test_formatting.py -v

# Run integration tests
docker compose exec api pytest tests/test_integration.py -v
```

## Testing

This project includes comprehensive unit and integration tests using pytest.

### Running Tests

#### With Docker
```bash
# Install test dependencies in container
docker compose exec api pip install pytest

# Run unit tests
docker compose exec api pytest tests/test_validation.py tests/test_formatting.py -v

# Run integration tests
docker compose exec api pytest tests/test_integration.py -v
```

#### Without Docker

**Install test dependencies:**
```bash
pip install pytest
```

**Run all tests:**
```bash
pytest tests/ -v
```

**Run specific test types:**
```bash
# Unit tests only
pytest tests/test_validation.py tests/test_formatting.py -v

# Integration tests only (requires running Flask server)
python app.py &  # Start server in background
pytest tests/test_integration.py -v
```

### Test Structure

- **Unit Tests** (`tests/test_validation.py`, `tests/test_formatting.py`)
  - Test individual functions in isolation
  - Validate data validation logic
  - Test data formatting functions
  - Test API key configuration
  - Fast execution, no external dependencies

- **Integration Tests** (`tests/test_integration.py`)
  - Test complete HTTP request/response workflows
  - Test database integration
  - Test authentication and authorization
  - Test error handling and edge cases
  - Require running Flask server

## CI/CD Integration

This project is designed to integrate seamlessly with Continuous Integration and Continuous Deployment (CI/CD) pipelines.

### GitHub Actions

GitHub Actions can be configured to automatically run tests on every push and pull request. A typical workflow would:

1. **Set up Python environment** - Install Python 3.9+ and dependencies from `requirements.txt`
2. **Run unit tests** - Execute `pytest tests/test_validation.py tests/test_formatting.py -v` for fast feedback
3. **Start Flask server** - Launch the API server in the background for integration testing
4. **Run integration tests** - Execute `pytest tests/test_integration.py -v` to test complete workflows
5. **Deploy on success** - Automatically deploy to staging or production when tests pass on main branch

The workflow could be configured to run on pushes to `main` and `develop` branches, as well as on pull requests, ensuring code quality before merging.

### CI/CD Example for This Project

1. **Automated Testing**
   - Run unit tests first (fast feedback)
   - Run integration tests after unit tests pass
   - Use test coverage reporting
   - Fail the pipeline if any tests fail

2. **Environment Management**
   - Use separate databases for testing and production
   - Set environment variables for different stages
   - Configure different API keys for each environment
   - Use containerization (Docker) for consistent environments

3. **Deployment Strategy**
   - Deploy to staging environment first
   - Run smoke tests after deployment
   - Use blue-green or rolling deployments for zero downtime
   - Implement rollback mechanisms

4. **Monitoring and Alerts**
   - Monitor the `/health` endpoint
   - Set up alerts for deployment failures
   - Track API response times and error rates
   - Monitor database performance

## Development

### Docker Development

**Start the application:**
```bash
docker-compose up
```

**Start in background:**
```bash
docker-compose up -d
```

**View logs:**
```bash
docker-compose logs -f
```

**Stop the application:**
```bash
docker-compose down
```

**Rebuild after code changes:**
```bash
docker-compose up --build
```

### Local Development

For local development without Docker, ensure you have Python 3.7+ installed and follow the Local Python installation steps above.

### Running Tests

#### With Docker
```bash
# Install test dependencies in container
docker-compose exec api pip install pytest

# Run unit tests
docker-compose exec api pytest tests/test_validation.py tests/test_formatting.py -v

# Run integration tests
docker-compose exec api pytest tests/test_integration.py -v
```

#### Without Docker
```bash
# Install test dependencies
pip install pytest

# Run all tests
pytest tests/ -v
```

### Project Structure
```
ubiety-take-home/
├── app.py                    # Main Flask application
├── requirements.txt          # Python dependencies
├── Dockerfile               # Docker container configuration
├── docker-compose.yml       # Docker Compose setup
├── .dockerignore            # Docker ignore file
├── device_status.db         # SQLite database (created automatically)
├── test_get_device.py       # Manual test script for GET /status/{device_id}
├── test_post.py             # Manual test script for POST /status
├── test_summary.py          # Manual test script for GET /status/summary
├── tests/
│   ├── __init__.py
│   ├── test_validation.py    # Unit tests for validation functions
│   ├── test_formatting.py    # Unit tests for formatting functions
│   └── test_integration.py   # Integration tests with pytest
└── README.md
```