# Redis Integration Guide

This document describes the Redis integration in the Krowoc backend, including the available features and how to use them.

## Setup

Redis is configured in `app.py` and requires the following environment variables:

```
REDIS_URL=redis://localhost:6379/0
```

In the development environment, Redis is provided via Docker Compose. For production, you should use a managed Redis service or a properly configured standalone Redis server.

## Features

### 1. Caching

The cache system provides function-level caching for any data that can be JSON serialized. 

#### Usage

```python
from backend.utils import cache

@cache(ttl=60)  # Cache results for 60 seconds
def expensive_function(user_id):
    # Expensive operation here
    return result
```

To invalidate the cache:

```python
from backend.utils import invalidate_cache

# Invalidate cache for a specific pattern
invalidate_cache("cache:expensive_function:*")
```

### 2. Pub/Sub (Publish/Subscribe)

The Pub/Sub system allows different components of the application to communicate asynchronously.

#### Publishing Events

```python
from backend.utils import RedisPubSub

# Publish an event
RedisPubSub.publish("channel_name", {
    "event_type": "user_registered",
    "user_id": 123,
    "timestamp": time.time()
})
```

#### Subscribing to Events

```python
from backend.utils import RedisPubSub

def handle_message(channel, message):
    print(f"Received on {channel}: {message}")

# Subscribe to channels (in a background thread)
def start_listener():
    RedisPubSub.subscribe(["channel_name"], handle_message)

import threading
thread = threading.Thread(target=start_listener, daemon=True)
thread.start()
```

### 3. Rate Limiting

The rate limiter helps protect APIs from abuse by limiting the number of requests from a single client.

#### Usage

```python
from backend.utils import RateLimiter

@app.route('/api/endpoint')
@RateLimiter.limit(requests_limit=100, time_window=60)  # 100 requests per minute
def my_api_endpoint():
    # Your API logic here
    return response
```

## Example Endpoints

The following example endpoints demonstrate Redis functionality:

1. **Cached Data**: `GET /api/cached-data`
   - Demonstrates caching of slow operations
   - Optional query parameter: `user_id`

2. **Cache Invalidation**: `POST /api/invalidate-cache`
   - Invalidates cache entries
   - Optional body parameter: `user_id` (to invalidate specific entries)

3. **Publish Event**: `POST /api/publish-event`
   - Publishes an event to a Redis channel
   - Required body parameters: `channel`, `message`

4. **Recent Events**: `GET /api/recent-events`
   - Lists recently received events from Redis Pub/Sub
   - Optional query parameters: `limit`, `channel`

5. **Rate Limited Endpoint**: `GET /api/rate-limited`
   - Demonstrates basic rate limiting (5 requests per minute)

6. **Slow Rate Limited Endpoint**: `GET /api/slow-limited`
   - Demonstrates stricter rate limiting for expensive operations (2 requests per 5 minutes)

## Health Checks

The Redis connection is monitored via the health check endpoints:

- `GET /health/deep` - Includes Redis connectivity status
- Redis memory usage is included in the health check response

## Best Practices

1. **Appropriate TTL**: Set cache expiration appropriately based on data volatility
2. **Invalidation**: Implement cache invalidation when data changes
3. **Serialization**: Ensure all data passed to Redis can be properly serialized/deserialized
4. **Error Handling**: All Redis utilities have fallbacks for when Redis is unavailable
5. **Performance Monitoring**: Monitor Redis memory usage and performance 