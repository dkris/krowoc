from flask import Flask
from flask_cors import CORS
import os
import platform
import datetime
import sys
import time
import psutil
from loguru import logger

# Track application start time for uptime calculation
APP_START_TIME = time.time()

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    
    # Configure CORS
    CORS(app)
    
    # Load configuration
    if test_config is None:
        app.config.from_mapping(
            SECRET_KEY=os.environ.get('SECRET_KEY', 'dev'),
            DATABASE_URL=os.environ.get('DATABASE_URL', 'postgresql://krowoc:krowoc@localhost:5432/krowoc'),
            REDIS_URL=os.environ.get('REDIS_URL', 'redis://localhost:6379/0'),
            VERSION=os.environ.get('VERSION', '0.1.0'),
        )
    else:
        app.config.from_mapping(test_config)
    
    # Register routes
    @app.route('/health')
    def health_check():
        return {
            'status': 'ok',
            'timestamp': datetime.datetime.now().isoformat()
        }
    
    @app.route('/health/detailed')
    def detailed_health_check():
        process = psutil.Process()
        return {
            'status': 'ok',
            'timestamp': datetime.datetime.now().isoformat(),
            'version': app.config.get('VERSION'),
            'system': {
                'platform': platform.platform(),
                'python_version': sys.version,
                'process_uptime_seconds': time.time() - APP_START_TIME,
                'memory_usage_percent': process.memory_percent()
            }
        }
    
    @app.route('/health/deep')
    def deep_health_check():
        status = 'ok'
        db_healthy = False
        redis_healthy = False
        
        # Check database connection
        try:
            # In a real implementation, we would attempt to connect to the database
            # For now, with test config we'll simulate a failure
            db_healthy = 'memory' not in str(app.config.get('DATABASE_URL', ''))
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
        
        # Check redis connection
        try:
            # In a real implementation, we would attempt to connect to Redis
            # For now, with test config we'll simulate a failure
            redis_healthy = app.config.get('REDIS_URL') is not None
        except Exception as e:
            logger.error(f"Redis health check failed: {str(e)}")
            
        # Determine overall status
        if not db_healthy or not redis_healthy:
            status = 'degraded'
        
        return {
            'status': status,
            'timestamp': datetime.datetime.now().isoformat(),
            'version': app.config.get('VERSION'),
            'checks': {
                'database': {
                    'healthy': db_healthy,
                    'message': 'Connected to database' if db_healthy else 'Failed to connect to database'
                },
                'redis': {
                    'healthy': redis_healthy,
                    'message': 'Connected to Redis' if redis_healthy else 'Failed to connect to Redis'
                }
            }
        }
    
    # Additional route registration will go here
    
    # Initialize logging
    logger.info("Application started")
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0') 