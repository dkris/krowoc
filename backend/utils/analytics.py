import os
import json
import uuid
import requests
from datetime import datetime
from flask import current_app, g, request
from .logging import get_contextual_logger

logger = get_contextual_logger()

# PostHog API key and host should be in environment variables
POSTHOG_API_KEY = os.environ.get('POSTHOG_API_KEY')
POSTHOG_HOST = os.environ.get('POSTHOG_HOST', 'https://app.posthog.com')

def get_correlation_id():
    """Get correlation ID from request or generate a new one"""
    # Check for correlation ID in headers
    if request and hasattr(request, 'headers'):
        # Try X-Correlation-ID (our standard) or X-Request-ID (for compatibility)
        correlation_id = request.headers.get('X-Correlation-ID') or request.headers.get('X-Request-ID')
        if correlation_id:
            return correlation_id
            
    # If not found in headers, check if already set in g
    if g and hasattr(g, 'correlation_id'):
        return g.correlation_id
        
    # Generate a new correlation ID
    return str(uuid.uuid4())

def set_correlation_id():
    """Set correlation ID in Flask g object"""
    if not hasattr(g, 'correlation_id'):
        g.correlation_id = get_correlation_id()
    return g.correlation_id

def track_event(event_name, properties=None, distinct_id=None):
    """Track an event in PostHog"""
    if not POSTHOG_API_KEY:
        logger.debug("PostHog API key not set, skipping event tracking")
        return
        
    if properties is None:
        properties = {}
        
    # Add correlation ID to properties
    if hasattr(g, 'correlation_id'):
        properties['correlation_id'] = g.correlation_id
    elif hasattr(request, 'headers') and request.headers.get('X-Correlation-ID'):
        properties['correlation_id'] = request.headers.get('X-Correlation-ID')
        
    # Add environment to properties
    properties['environment'] = os.environ.get('FLASK_ENV', 'development')
    
    # Add user ID if available
    if hasattr(g, 'user_id') and g.user_id and not distinct_id:
        distinct_id = g.user_id
        
    # If still no distinct_id, generate one
    if not distinct_id:
        distinct_id = "backend-server"
        
    # Prepare the payload
    payload = {
        'api_key': POSTHOG_API_KEY,
        'event': event_name,
        'properties': properties,
        'distinct_id': distinct_id,
        'timestamp': datetime.now().isoformat()
    }
    
    # In development mode, just log the event
    if os.environ.get('FLASK_ENV') != 'production':
        logger.debug("Would send PostHog event: {}", json.dumps(payload))
        return
        
    # Send the event to PostHog
    try:
        requests.post(
            f"{POSTHOG_HOST}/capture/", 
            json=payload,
            timeout=1.0  # Short timeout to not block the request
        )
        logger.debug("PostHog event sent: {}", event_name)
    except Exception as e:
        logger.error("Failed to send PostHog event: {} - {}", event_name, str(e))

def identify_user(user_id, properties=None):
    """Identify a user in PostHog"""
    if not POSTHOG_API_KEY or not user_id:
        return
        
    if properties is None:
        properties = {}
        
    # In development mode, just log the identification
    if os.environ.get('FLASK_ENV') != 'production':
        logger.debug("Would identify PostHog user: {} with properties: {}", user_id, properties)
        return
        
    # Send the identify call to PostHog
    try:
        payload = {
            'api_key': POSTHOG_API_KEY,
            'distinct_id': user_id,
            'properties': properties
        }
        requests.post(
            f"{POSTHOG_HOST}/identify/",
            json=payload,
            timeout=1.0
        )
        logger.debug("PostHog user identified: {}", user_id)
    except Exception as e:
        logger.error("Failed to identify PostHog user: {} - {}", user_id, str(e))

def track_api_request(endpoint, method, response_status):
    """Track an API request in PostHog"""
    track_event('api_request', {
        'endpoint': endpoint,
        'method': method,
        'status': response_status,
        'user_agent': request.user_agent.string if request.user_agent else "Unknown"
    })
    
def track_prompt_execution(prompt_id, model, token_count, success, duration_ms):
    """Track a prompt execution in PostHog"""
    track_event('prompt_execution', {
        'prompt_id': prompt_id,
        'model': model,
        'token_count': token_count,
        'success': success,
        'duration_ms': duration_ms
    })
    
def track_login(user_id, provider, success, error=None):
    """Track a login event in PostHog"""
    properties = {
        'provider': provider,
        'success': success
    }
    
    if error and not success:
        # Only include non-sensitive error information
        properties['error_type'] = error
        
    track_event('login', properties, user_id)

def track_error(error_type, message, context=None):
    """Track an error in PostHog"""
    properties = {
        'error_type': error_type,
        'message': message,
    }
    
    if context:
        properties['context'] = context
        
    track_event('error', properties) 