import redis
from flask import current_app
import json
from typing import Any, Optional, Dict, List, Callable
from functools import wraps
import time
from loguru import logger

# Singleton Redis client instance
_redis_client = None


def get_redis_client():
    """
    Get or create the Redis client singleton instance
    
    Returns:
        redis.Redis: The Redis client
    """
    global _redis_client
    
    if _redis_client is None:
        redis_url = current_app.config.get('REDIS_URL')
        if not redis_url:
            logger.warning("Redis URL not configured")
            return None
            
        _redis_client = redis.from_url(redis_url, decode_responses=True)
    
    return _redis_client


def cache(ttl: int = 300):
    """
    Decorator for caching function results in Redis
    
    Args:
        ttl (int): Time to live in seconds (default: 300s / 5min)
        
    Returns:
        Callable: Decorated function
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get Redis client
            client = get_redis_client()
            if not client:
                # If no client available, just call the original function
                return func(*args, **kwargs)
                
            # Generate a cache key from function name and arguments
            key_parts = [func.__name__]
            # Add positional args to key
            key_parts.extend([str(arg) for arg in args])
            # Add keyword args to key
            key_parts.extend([f"{k}:{v}" for k, v in sorted(kwargs.items())])
            cache_key = f"cache:{':'.join(key_parts)}"
            
            # Try to get from cache
            cached_data = client.get(cache_key)
            if cached_data:
                try:
                    return json.loads(cached_data)
                except (json.JSONDecodeError, TypeError):
                    # If cached data can't be decoded, log and proceed without cache
                    logger.warning(f"Failed to decode cached data for key: {cache_key}")
            
            # Execute the function and cache the result
            result = func(*args, **kwargs)
            
            try:
                # Only cache if result is JSON serializable
                client.setex(cache_key, ttl, json.dumps(result))
            except (TypeError, ValueError) as e:
                logger.warning(f"Failed to cache result: {e}")
                
            return result
        return wrapper
    return decorator


def invalidate_cache(pattern: str = None):
    """
    Invalidate cache entries matching the given pattern
    
    Args:
        pattern (str, optional): Pattern to match (e.g., "cache:get_user:*")
                                If None, does nothing
    """
    if not pattern:
        return
        
    client = get_redis_client()
    if not client:
        return
        
    keys = client.keys(pattern)
    if keys:
        client.delete(*keys)
        logger.info(f"Invalidated {len(keys)} cache entries matching: {pattern}")


class RedisPubSub:
    """Redis Publish/Subscribe functionality"""
    
    @staticmethod
    def publish(channel: str, message: Any):
        """
        Publish a message to a Redis channel
        
        Args:
            channel (str): Channel name
            message (Any): Message to publish (will be JSON serialized)
            
        Returns:
            int: Number of clients that received the message
        """
        client = get_redis_client()
        if not client:
            return 0
            
        try:
            payload = json.dumps(message)
            return client.publish(channel, payload)
        except (TypeError, ValueError) as e:
            logger.error(f"Failed to publish message: {e}")
            return 0
    
    @staticmethod
    def subscribe(channels: List[str], callback: Callable[[str, dict], None]):
        """
        Subscribe to Redis channels and process messages with a callback
        
        NOTE: This method will block the current thread. It should be run in a 
        separate thread or process.
        
        Args:
            channels (List[str]): List of channel names to subscribe to
            callback (Callable): Function to call for each message
                                Function signature: callback(channel, message)
        """
        client = get_redis_client()
        if not client:
            return
            
        pubsub = client.pubsub()
        pubsub.subscribe(channels)
        
        logger.info(f"Subscribed to Redis channels: {channels}")
        
        for message in pubsub.listen():
            if message['type'] == 'message':
                channel = message['channel']
                try:
                    data = json.loads(message['data'])
                    callback(channel, data)
                except (json.JSONDecodeError, TypeError) as e:
                    logger.error(f"Failed to process Redis message: {e}") 