from flask import Flask
from flask_cors import CORS
import os
from loguru import logger

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
        )
    else:
        app.config.from_mapping(test_config)
    
    # Register routes
    @app.route('/health')
    def health_check():
        return {'status': 'ok'}
    
    # Additional route registration will go here
    
    # Initialize logging
    logger.info("Application started")
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0') 