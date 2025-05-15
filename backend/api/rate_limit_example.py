from flask import Blueprint, jsonify
import time
from ..utils.rate_limiter import RateLimiter
from ..utils.logging import get_contextual_logger

# Create blueprint
rate_limit_bp = Blueprint('rate_limit', __name__)
logger = get_contextual_logger()

@rate_limit_bp.route('/api/rate-limited', methods=['GET'])
@RateLimiter.limit(requests_limit=5, time_window=60, key_prefix='demo')
def rate_limited_endpoint():
    """
    Example endpoint demonstrating rate limiting
    
    This endpoint has a limit of 5 requests per minute per client.
    Clients are identified by IP address by default.
    """
    logger.info("Handling rate-limited request")
    
    return jsonify({
        'message': 'This endpoint is rate limited to 5 requests per minute',
        'timestamp': time.time()
    })

@rate_limit_bp.route('/api/slow-limited', methods=['GET'])
@RateLimiter.limit(requests_limit=2, time_window=300, key_prefix='slow_api')
def slow_limited_endpoint():
    """
    Example of a slow endpoint with stricter rate limiting
    
    This endpoint has a limit of 2 requests per 5 minutes per client.
    """
    logger.info("Processing slow rate-limited request")
    
    # Simulate slow operation
    time.sleep(3)
    
    return jsonify({
        'message': 'This is a slow endpoint limited to 2 requests per 5 minutes',
        'timestamp': time.time(),
        'computed_at': time.ctime()
    }) 