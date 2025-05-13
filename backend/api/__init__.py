from flask import Blueprint
from .health import health_bp

# Create a parent blueprint for all API routes
api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

# Import and register other API modules/blueprints here
# Example: from .users import users_bp

def register_blueprints(app):
    """Register all blueprints with the Flask app"""
    # Register the health blueprint without prefix (for standard health check endpoints)
    app.register_blueprint(health_bp)
    
    # Register the main API blueprint
    app.register_blueprint(api_bp)
    
    # Register other API components to the api_blueprint
    # Example: api_bp.register_blueprint(users_bp) 