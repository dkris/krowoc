from flask import g, request, jsonify
from functools import wraps
from .db import get_db
from ..models.user import User
from ..models.api_key import ApiKey

def authenticate(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get auth token from request
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({"error": "No authorization header provided"}), 401
        
        try:
            # Format should be "Bearer <token>"
            token_parts = auth_header.split()
            if len(token_parts) != 2 or token_parts[0].lower() != 'bearer':
                return jsonify({"error": "Invalid authorization header format"}), 401
            
            token = token_parts[1]
            
            # In a real application, you would validate the token
            # For this example, we'll just check if it exists in the database
            db = get_db()
            api_key = db.query(ApiKey).filter(ApiKey.key == token).first()
            
            if not api_key:
                return jsonify({"error": "Invalid API key"}), 401
            
            # Get the user for this API key
            user = db.query(User).filter(User.id == api_key.user_id).first()
            
            if not user:
                return jsonify({"error": "User not found"}), 401
            
            if not user.is_active:
                return jsonify({"error": "User account is inactive"}), 403
            
            # Store user in Flask's g object for this request
            g.user = user
            
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
            
    return decorated_function 