from flask import Blueprint, jsonify, request
import time
from ..utils.redis_client import cache, invalidate_cache, RedisPubSub
from ..utils.logging import get_contextual_logger

# Create blueprint
cache_bp = Blueprint('cache', __name__)
logger = get_contextual_logger()

@cache_bp.route('/api/cached-data', methods=['GET'])
@cache(ttl=60)  # Cache results for 60 seconds
def get_cached_data():
    """
    Example endpoint demonstrating Redis caching
    
    This simulates a slow operation (like a database query or external API call)
    that we want to cache to improve performance.
    """
    logger.info("Processing cached data request")
    
    # Get request parameters
    user_id = request.args.get('user_id', 'anonymous')
    
    # Simulate a slow operation
    logger.info(f"Performing expensive operation for user_id={user_id}")
    time.sleep(2)  # Simulate 2 second delay
    
    # Generate response data
    data = {
        'user_id': user_id,
        'timestamp': time.time(),
        'message': f"This response is cached for 60 seconds for user {user_id}",
        'computed_at': time.ctime()
    }
    
    return jsonify(data)


@cache_bp.route('/api/invalidate-cache', methods=['POST'])
def invalidate_example_cache():
    """
    Invalidate the cache for a specific user or all users
    
    POST parameters:
        user_id: Optional - The user ID to invalidate
                 If not provided, invalidates for all users
    """
    # Get user_id from request
    user_id = request.json.get('user_id')
    
    if user_id:
        # Invalidate cache for specific user
        pattern = f"cache:get_cached_data:*{user_id}*"
        invalidate_cache(pattern)
        logger.info(f"Invalidated cache for user_id={user_id}")
        message = f"Cache invalidated for user {user_id}"
    else:
        # Invalidate all cached data
        invalidate_cache("cache:get_cached_data:*")
        logger.info("Invalidated all cached data")
        message = "All cache entries invalidated"
    
    # Publish event to Redis
    RedisPubSub.publish('cache_events', {
        'action': 'invalidate',
        'user_id': user_id,
        'timestamp': time.time()
    })
    
    return jsonify({'success': True, 'message': message}) 