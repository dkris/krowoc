import pytest
from flask import url_for, g
import uuid
import json
from backend.app import create_app

@pytest.fixture
def app():
    """Create and configure a Flask app for testing."""
    app = create_app({
        'TESTING': True,
        'DATABASE_URI': 'sqlite:///:memory:',
        'REDIS_URL': None,
        'POSTHOG_API_KEY': 'test_key'
    })
    
    # Create a test endpoint for correlation ID testing
    @app.route('/api/v1/test-correlation')
    def test_correlation():
        # Return correlation ID for testing
        return {
            'correlation_id': g.correlation_id if hasattr(g, 'correlation_id') else None,
            'request_id': g.request_id if hasattr(g, 'request_id') else None
        }
    
    yield app

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

def test_correlation_id_generation(client):
    """Test that correlation ID is generated when not provided."""
    response = client.get('/api/v1/test-correlation')
    assert response.status_code == 200
    data = json.loads(response.data)
    
    # Check that a correlation ID was generated
    assert data['correlation_id'] is not None
    assert len(data['correlation_id']) > 0
    
    # Check that correlation ID was added to response headers
    assert 'X-Correlation-ID' in response.headers
    assert response.headers['X-Correlation-ID'] == data['correlation_id']

def test_correlation_id_propagation(client):
    """Test that provided correlation ID is propagated."""
    test_id = str(uuid.uuid4())
    response = client.get(
        '/api/v1/test-correlation',
        headers={'X-Correlation-ID': test_id}
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    
    # Check that the correlation ID was preserved
    assert data['correlation_id'] == test_id
    
    # Check that correlation ID was added to response headers
    assert 'X-Correlation-ID' in response.headers
    assert response.headers['X-Correlation-ID'] == test_id

def test_request_id_use(client):
    """Test that X-Request-ID is used as fallback."""
    test_id = str(uuid.uuid4())
    response = client.get(
        '/api/v1/test-correlation',
        headers={'X-Request-ID': test_id}
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    
    # Check that the request ID was used as correlation ID
    assert data['correlation_id'] == test_id
    assert data['request_id'] == test_id
    
    # Check that correlation ID was added to response headers
    assert 'X-Correlation-ID' in response.headers
    assert response.headers['X-Correlation-ID'] == test_id

def test_correlation_id_consistency(client):
    """Test that correlation ID is consistent across multiple requests in the same flow."""
    # First request to get a correlation ID
    test_id = str(uuid.uuid4())
    response1 = client.get(
        '/api/v1/test-correlation',
        headers={'X-Correlation-ID': test_id}
    )
    
    # Second request with the same correlation ID
    response2 = client.get(
        '/api/v1/test-correlation',
        headers={'X-Correlation-ID': test_id}
    )
    
    data1 = json.loads(response1.data)
    data2 = json.loads(response2.data)
    
    # Both requests should have the same correlation ID
    assert data1['correlation_id'] == test_id
    assert data2['correlation_id'] == test_id
    assert response1.headers['X-Correlation-ID'] == response2.headers['X-Correlation-ID'] 