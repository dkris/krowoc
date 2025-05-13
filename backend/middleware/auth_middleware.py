from functools import wraps
from flask import request, jsonify, g, current_app
from loguru import logger
from ..services.auth_service import AuthService
from sqlalchemy.orm import Session
from typing import Callable, Any

def get_db_session() -> Session:
    """
    Helper function to get database session from Flask g object
    """
    if 'db_session' not in g:
        # This would be configured elsewhere in your application
        raise RuntimeError("Database session not available in Flask context")
    return g.db_session

def login_required(f: Callable) -> Callable:
    """
    Decorator to protect routes that require authentication
    """
    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Any:
        try:
            db_session = get_db_session()
            auth_service = AuthService(db_session)
            current_user = auth_service.get_current_user()
            
            if not current_user:
                return jsonify({"error": "Authentication required"}), 401
                
            # Store user in Flask g object for route handlers
            g.current_user = current_user
            return f(*args, **kwargs)
            
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return jsonify({"error": "Authentication error"}), 500
            
    return decorated_function 