from functools import wraps
from flask import request, jsonify, current_app
import time
from .redis_client import get_redis_client
from .logging import get_contextual_logger

logger = get_contextual_logger()

class RateLimiter:
    """Rate limiting implementation using Redis"""
    
    @staticmethod
    def limit(requests_limit=100, time_window=60, key_prefix='rate_limit'):
        """
        Decorator to apply rate limiting to Flask routes
        
        Args:
            requests_limit (int): Maximum number of requests allowed in the time window
            time_window (int): Time window in seconds
            key_prefix (str): Prefix for Redis keys
            
        Returns:
            Callable: Decorated route function
        """
        def decorator(f):
            @wraps(f)
            def wrapped_function(*args, **kwargs):
                # Get Redis client
                redis_client = get_redis_client()
                if not redis_client:
                    # If Redis not available, let the request through
                    logger.warning("Redis not available for rate limiting")
                    return f(*args, **kwargs)
                
                # Determine rate limit key
                # Default client identifier is IP address
                client_id = request.headers.get('X-Forwarded-For', request.remote_addr)
                
                # Allow for custom identifiers (like API key or user ID)
                if hasattr(request, 'user_id') and request.user_id:
                    client_id = f"user:{request.user_id}"
                elif request.headers.get('X-API-Key'):
                    client_id = f"apikey:{request.headers.get('X-API-Key')}"
                
                # Create Redis key
                key = f"{key_prefix}:{client_id}:{request.path}"
                
                # Get current count and increment
                pipe = redis_client.pipeline()
                pipe.incr(key)
                pipe.expire(key, time_window)  # Reset after time window
                result = pipe.execute()
                
                current_count = result[0]
                
                # Check if rate limit exceeded
                if current_count > requests_limit:
                    logger.warning(f"Rate limit exceeded for {client_id} on {request.path}")
                    
                    # Calculate reset time
                    ttl = redis_client.ttl(key)
                    reset_time = int(time.time() + ttl)
                    
                    # Return rate limit exceeded response
                    response = jsonify({
                        'error': 'Rate limit exceeded',
                        'limit': requests_limit,
                        'remaining': 0,
                        'reset': reset_time
                    })
                    response.status_code = 429  # Too Many Requests
                    return response
                
                # Add rate limit headers to response
                response = f(*args, **kwargs)
                
                # If response is not already a Response object (e.g., a tuple), let it through
                if not hasattr(response, 'headers'):
                    return response
                
                # Add rate limit headers
                ttl = redis_client.ttl(key)
                reset_time = int(time.time() + ttl)
                
                response.headers['X-RateLimit-Limit'] = str(requests_limit)
                response.headers['X-RateLimit-Remaining'] = str(max(0, requests_limit - current_count))
                response.headers['X-RateLimit-Reset'] = str(reset_time)
                
                return response
            return wrapped_function
        return decorator 