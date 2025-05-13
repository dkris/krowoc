from flask import Flask, g
from flask_cors import CORS
import os
from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from dotenv import load_dotenv
from api.auth import auth_bp

# Load environment variables
load_dotenv()

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
            SUPABASE_URL=os.environ.get('SUPABASE_URL', ''),
            SUPABASE_KEY=os.environ.get('SUPABASE_KEY', ''),
            SUPABASE_JWT_SECRET=os.environ.get('SUPABASE_JWT_SECRET', ''),
        )
    else:
        app.config.from_mapping(test_config)
    
    # Set up database connection
    engine = create_engine(app.config['DATABASE_URL'])
    session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Session = scoped_session(session_factory)
    
    @app.before_request
    def before_request():
        g.db_session = Session()
    
    @app.teardown_appcontext
    def teardown_appcontext(exception=None):
        if hasattr(g, 'db_session'):
            g.db_session.close()
    
    # Register routes
    @app.route('/health')
    def health_check():
        return {'status': 'ok'}
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    
    # Initialize logging
    logger.info("Application started")
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0') 