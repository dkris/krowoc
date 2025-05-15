from flask import Blueprint
from .health import health_bp
from .graphql import graphql_bp
from .prompts import prompt_blueprint
from .cache_example import cache_bp
from .pubsub_example import pubsub_bp
from .rate_limit_example import rate_limit_bp
from .usage_metrics import bp as usage_metrics_bp

# Create a parent blueprint for all API routes
api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

# Import and register other API modules/blueprints here
# Example: from .users import users_bp

def register_blueprints(app):
    """Register all blueprints with the Flask app"""
    # Register the health blueprint without prefix (for standard health check endpoints)
    app.register_blueprint(health_bp)
    
    # Register the GraphQL blueprint
    app.register_blueprint(graphql_bp, url_prefix='/api/v1')
    
    # Register the prompts blueprint
    app.register_blueprint(prompt_blueprint)
    
    # Register Redis example blueprints
    app.register_blueprint(cache_bp)
    app.register_blueprint(pubsub_bp)
    app.register_blueprint(rate_limit_bp)
    
    # Register usage metrics blueprint
    app.register_blueprint(usage_metrics_bp)
    
    # Register the main API blueprint
    app.register_blueprint(api_bp)
    
    # Register other API components to the api_blueprint
    # Example: api_bp.register_blueprint(users_bp) 