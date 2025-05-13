import pytest
from flask import Flask
import json
import datetime
from app import create_app

@pytest.fixture
def app():
    """Create and configure a Flask app for testing."""
    app = create_app({
        'TESTING': True,
        'DATABASE_URL': 'sqlite:///:memory:',
        'REDIS_URL': None,
    })
    yield app
    
@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

def test_basic_health(client):
    """Test that the basic health check endpoint works."""
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'ok'
    assert 'timestamp' in data

def test_detailed_health(client):
    """Test that the detailed health check endpoint works."""
    response = client.get('/health/detailed')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'ok'
    assert 'timestamp' in data
    assert 'version' in data
    assert 'system' in data
    assert 'platform' in data['system']
    assert 'python_version' in data['system']
    assert 'process_uptime_seconds' in data['system']
    assert 'memory_usage_percent' in data['system']

def test_deep_health(client):
    """Test that the deep health check endpoint works with mocked subsystems."""
    response = client.get('/health/deep')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'status' in data
    assert 'timestamp' in data
    assert 'version' in data
    assert 'checks' in data
    assert 'database' in data['checks']
    assert 'redis' in data['checks']
    
    # Since we're using a test config with invalid DB/Redis URLs,
    # we expect these checks to fail
    assert data['checks']['database']['healthy'] is False
    assert data['checks']['redis']['healthy'] is False
    assert data['status'] == 'degraded' 