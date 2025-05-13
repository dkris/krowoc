from flask import Blueprint, jsonify, g, request
from loguru import logger
from ..services.auth_service import AuthService
from ..middleware.auth_middleware import login_required

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/me', methods=['GET'])
@login_required
def get_current_user():
    """
    Get information about the currently authenticated user
    """
    user = g.current_user
    
    return jsonify({
        "id": user.id,
        "email": user.email,
        "display_name": user.display_name,
        "avatar_url": user.avatar_url,
        "auth_provider": user.auth_provider,
        "is_active": user.is_active,
        "created_at": user.created_at.isoformat() if user.created_at else None,
    })

@auth_bp.route('/verify', methods=['POST'])
def verify_token():
    """
    Verify a JWT token without requiring authentication
    """
    try:
        data = request.get_json()
        token = data.get('token')
        
        if not token:
            return jsonify({"error": "Token is required"}), 400
            
        auth_service = AuthService(g.db_session)
        
        # Temporarily set the token in the Authorization header
        original_auth = request.headers.get('Authorization')
        request.headers = {**request.headers, 'Authorization': f'Bearer {token}'}
        
        user = auth_service.get_current_user()
        
        # Restore original Authorization header
        if original_auth:
            request.headers = {**request.headers, 'Authorization': original_auth}
        else:
            # Remove the Authorization header if there wasn't one
            request.headers.pop('Authorization', None)
            
        if user:
            return jsonify({"valid": True, "user_id": user.id})
        else:
            return jsonify({"valid": False}), 401
            
    except Exception as e:
        logger.error(f"Token verification error: {str(e)}")
        return jsonify({"error": "Failed to verify token"}), 500 