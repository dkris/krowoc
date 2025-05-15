from flask import Blueprint, jsonify, request
import time
import threading
from ..utils.redis_client import RedisPubSub, get_redis_client
from ..utils.logging import get_contextual_logger

# Create blueprint
pubsub_bp = Blueprint('pubsub', __name__)
logger = get_contextual_logger()

# Global storage for received messages (for demo purposes)
RECEIVED_MESSAGES = []
MAX_STORED_MESSAGES = 100

# Initialize subscriber in a background thread
def start_subscriber():
    """Start the Redis subscriber in a background thread"""
    def message_handler(channel, message):
        """Handle incoming Redis messages"""
        logger.info(f"Received message on channel {channel}: {message}")
        
        # Store message for retrieval via API
        timestamp = time.time()
        RECEIVED_MESSAGES.append({
            'channel': channel,
            'message': message,
            'received_at': timestamp,
            'received_at_formatted': time.ctime(timestamp)
        })
        
        # Keep message list at manageable size
        while len(RECEIVED_MESSAGES) > MAX_STORED_MESSAGES:
            RECEIVED_MESSAGES.pop(0)
    
    def subscriber_thread():
        """Background thread function for Redis subscription"""
        logger.info("Starting Redis subscriber thread")
        # Subscribe to multiple channels
        RedisPubSub.subscribe(['events', 'notifications', 'cache_events'], message_handler)
    
    # Start the thread
    thread = threading.Thread(target=subscriber_thread, daemon=True)
    thread.start()
    logger.info("Redis subscriber thread started")

# Start the subscriber when this module is imported
start_subscriber()

@pubsub_bp.route('/api/publish-event', methods=['POST'])
def publish_event():
    """
    Publish an event to a Redis channel
    
    POST parameters:
        channel: The channel to publish to
        message: The message payload to publish
    """
    data = request.json
    if not data:
        return jsonify({'error': 'No JSON data provided'}), 400
    
    channel = data.get('channel')
    message = data.get('message')
    
    if not channel:
        return jsonify({'error': 'No channel specified'}), 400
    if not message:
        return jsonify({'error': 'No message specified'}), 400
    
    # Publish the message
    recipients = RedisPubSub.publish(channel, message)
    
    return jsonify({
        'success': True,
        'channel': channel,
        'recipients': recipients,
        'timestamp': time.time()
    })

@pubsub_bp.route('/api/recent-events', methods=['GET'])
def get_recent_events():
    """Get recently received events from Redis Pub/Sub"""
    limit = request.args.get('limit', default=10, type=int)
    channel = request.args.get('channel')
    
    # Filter by channel if requested
    if channel:
        filtered_messages = [msg for msg in RECEIVED_MESSAGES if msg['channel'] == channel]
    else:
        filtered_messages = RECEIVED_MESSAGES
    
    # Return most recent messages first, limited to requested count
    recent_messages = sorted(
        filtered_messages,
        key=lambda x: x['received_at'],
        reverse=True
    )[:limit]
    
    return jsonify({
        'channel_filter': channel,
        'limit': limit,
        'count': len(recent_messages),
        'events': recent_messages
    }) 