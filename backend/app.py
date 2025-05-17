from flask import Flask, request, g
from flask_cors import CORS
import os
import platform
import datetime
import sys
import time
import psutil
from loguru import logger

# Import API module for blueprint registration
from backend.api import register_blueprints
from backend.utils.db import init_app as init_db
from backend.utils.logging import setup_logging
from backend.utils.middleware import RequestLoggingMiddleware, setup_request_context, teardown_request_context

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
            DATABASE_URI=os.environ.get('DATABASE_URL', 'postgresql://krowoc:krowoc@localhost:5432/krowoc'),
            REDIS_URL=os.environ.get('REDIS_URL', 'redis://localhost:6379/0'),
            VERSION=os.environ.get('VERSION', '1.2.0'),
            POSTHOG_API_KEY=os.environ.get('POSTHOG_API_KEY', ''),
            POSTHOG_HOST=os.environ.get('POSTHOG_HOST', 'https://app.posthog.com'),
        )
    else:
        app.config.from_mapping(test_config)
    
    # Initialize logging
    setup_logging()
    
    # Initialize database
    init_db(app)
    
    # Register request tracking middleware
    app.wsgi_app = RequestLoggingMiddleware(app.wsgi_app)
    
    # Register before/after request handlers for request context
    @app.before_request
    def before_request():
        setup_request_context()
    
    @app.after_request
    def after_request(response):
        return teardown_request_context(response)
    
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
            db_healthy = 'memory' not in str(app.config.get('DATABASE_URI', ''))
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
    
    # Register error handlers
    @app.errorhandler(404)
    def not_found(error):
        from backend.utils.analytics import track_error
        track_error("not_found", f"Route not found: {request.path}")
        return {"error": "Not Found", "message": "The requested resource was not found"}, 404
    
    @app.errorhandler(500)
    def server_error(error):
        from backend.utils.analytics import track_error
        track_error("server_error", str(error), {"path": request.path})
        return {"error": "Internal Server Error", "message": "An unexpected error occurred"}, 500
    
    # Register blueprints using the central registration function
    register_blueprints(app)
    
    logger.info("Application started")
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0') 