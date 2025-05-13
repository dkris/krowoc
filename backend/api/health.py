from flask import Blueprint, current_app, jsonify
import time
import platform
import psutil
import os
import datetime
import sqlalchemy
from sqlalchemy import text
from ..utils.logging import get_contextual_logger

# Create Blueprint for health check routes
health_bp = Blueprint('health', __name__)
logger = get_contextual_logger()

# Basic health check that returns quickly
@health_bp.route('/health', methods=['GET'])
def basic_health():
    """Simple health check endpoint"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.datetime.utcnow().isoformat(),
    })

# More detailed health check
@health_bp.route('/health/detailed', methods=['GET'])
def detailed_health():
    """Detailed health check with system information"""
    health_data = {
        'status': 'ok',
        'timestamp': datetime.datetime.utcnow().isoformat(),
        'version': os.environ.get('APP_VERSION', 'development'),
        'system': {
            'platform': platform.platform(),
            'python_version': platform.python_version(),
            'process_uptime_seconds': time.time() - psutil.Process(os.getpid()).create_time(),
            'memory_usage_percent': psutil.Process(os.getpid()).memory_percent(),
        }
    }
    
    return jsonify(health_data)

# Deep health check including database connectivity
@health_bp.route('/health/deep', methods=['GET'])
def deep_health():
    """Deep health check including subsystem verifications"""
    health_data = {
        'status': 'ok',
        'timestamp': datetime.datetime.utcnow().isoformat(),
        'version': os.environ.get('APP_VERSION', 'development'),
        'checks': {
            'database': check_database_connection(),
            'redis': check_redis_connection(),
        }
    }
    
    # If any subsystem is not healthy, set overall status to degraded
    if not all(check['healthy'] for check in health_data['checks'].values()):
        health_data['status'] = 'degraded'
        
    return jsonify(health_data)

def check_database_connection():
    """Check if database is accessible"""
    try:
        # Get database URL from app config
        db_url = current_app.config.get('DATABASE_URL')
        if not db_url:
            return {'healthy': False, 'error': 'No database URL configured'}
        
        # Create engine and try a simple query
        engine = sqlalchemy.create_engine(db_url)
        with engine.connect() as conn:
            conn.execute(text('SELECT 1'))
        
        return {'healthy': True}
    except Exception as e:
        logger.exception("Database health check failed")
        return {'healthy': False, 'error': str(e)}

def check_redis_connection():
    """Check if Redis is accessible"""
    try:
        # Import redis here to avoid import error if not used
        import redis
        
        # Get Redis URL from app config
        redis_url = current_app.config.get('REDIS_URL')
        if not redis_url:
            return {'healthy': False, 'error': 'No Redis URL configured'}
        
        # Create client and ping
        r = redis.from_url(redis_url)
        r.ping()
        
        return {'healthy': True}
    except Exception as e:
        logger.exception("Redis health check failed")
        return {'healthy': False, 'error': str(e)} 