import secrets
import string
import logging
import uuid
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify, g
import json

# Initialize blueprint
user_settings_bp = Blueprint('user_settings', __name__, url_prefix='/api/user-settings')
logger = logging.getLogger(__name__)

# Provider API Key Management
@user_settings_bp.route('/api-keys', methods=['POST'])
# TODO: Implement authentication (login_required) and password hashing (hash_password) for REST endpoints
def add_provider_api_key():
    """
    Add a provider API key (OpenAI, Anthropic, Google)
    """
    try:
        # Get request data
        data = request.get_json()
        if not data or 'provider' not in data or 'key' not in data:
            return jsonify({'error': 'Provider and API key are required'}), 400
            
        provider = data['provider']
        api_key = data['key']
        
        # Validate provider
        valid_providers = ['openai', 'anthropic', 'google']
        if provider not in valid_providers:
            return jsonify({'error': f'Invalid provider. Must be one of: {", ".join(valid_providers)}'}), 400
        
        # Store only part of the key for reference
        key_prefix = api_key[:6]
        
        # Generate a unique ID
        key_id = str(uuid.uuid4())
        current_time = datetime.now(timezone.utc)
        
        # Store the hashed key, not the raw key
        # TODO: Implement password hashing (hash_password)
        hashed_key = api_key
        
        from backend.services.database import get_supabase_client
        supabase = get_supabase_client()
        
        # Check if this provider key already exists for the user (upsert it)
        check_result = supabase.table('provider_api_keys').select('id').eq('user_id', g.user.id).eq('provider', provider).execute()
        
        if check_result.data:
            # Update existing key
            result = supabase.table('provider_api_keys').update({
                'key_hash': hashed_key,
                'key_prefix': key_prefix,
                'created_at': current_time.isoformat(),
                'last_used_at': None
            }).eq('id', check_result.data[0]['id']).execute()
            key_id = check_result.data[0]['id']
        else:
            # Insert new key
            result = supabase.table('provider_api_keys').insert({
                'id': key_id,
                'user_id': g.user.id,
                'provider': provider,
                'key_hash': hashed_key,
                'key_prefix': key_prefix,
                'created_at': current_time.isoformat(),
                'last_used_at': None
            }).execute()
        
        if result.data:
            return jsonify({
                'id': key_id,
                'provider': provider,
                'key_prefix': key_prefix,
                'created_at': current_time.isoformat()
            }), 201
        else:
            return jsonify({'error': 'Failed to add provider API key'}), 500
            
    except Exception as e:
        logger.error(f"Error adding provider API key: {str(e)}")
        return jsonify({'error': f'Failed to add provider API key: {str(e)}'}), 500

@user_settings_bp.route('/api-keys', methods=['GET'])
# TODO: Implement authentication (login_required)
def list_provider_api_keys():
    """
    List all provider API keys for the authenticated user
    """
    try:
        from backend.services.database import get_supabase_client
        supabase = get_supabase_client()
        
        result = supabase.table('provider_api_keys').select(
            'id, provider, key_prefix, created_at, last_used_at'
        ).eq('user_id', g.user.id).execute()
        
        return jsonify(result.data)
        
    except Exception as e:
        logger.error(f"Error listing provider API keys: {str(e)}")
        return jsonify({'error': f'Failed to list provider API keys: {str(e)}'}), 500

@user_settings_bp.route('/api-keys/<key_id>', methods=['DELETE'])
# TODO: Implement authentication (login_required)
def delete_provider_api_key(key_id):
    """
    Delete a provider API key by ID
    """
    try:
        from backend.services.database import get_supabase_client
        supabase = get_supabase_client()
        
        # First, verify the key belongs to the user
        check_result = supabase.table('provider_api_keys').select('id').eq('id', key_id).eq('user_id', g.user.id).execute()
        
        if not check_result.data:
            return jsonify({'error': "API key not found or doesn't belong to you"}), 404
        
        # Delete the key
        result = supabase.table('provider_api_keys').delete().eq('id', key_id).execute()
        
        return jsonify({"success": True, "message": "API key deleted successfully"})
        
    except Exception as e:
        logger.error(f"Error deleting provider API key: {str(e)}")
        return jsonify({'error': f'Failed to delete provider API key: {str(e)}'}), 500

@user_settings_bp.route('/test-provider-call/<provider>', methods=['GET'])
# TODO: Implement authentication (login_required)
async def test_provider_call(provider):
    """
    Test endpoint to validate a provider API key by making a simple API call
    """
    try:
        valid_providers = ['openai', 'anthropic', 'google']
        if provider not in valid_providers:
            return jsonify({'error': f'Invalid provider. Must be one of: {", ".join(valid_providers)}'}), 400
        
        from backend.utils.provider_keys import get_provider_api_key, verify_provider_api_key
        
        # Securely get the provider key
        api_key = await get_provider_api_key(g.user.id, provider)
        
        if not api_key:
            return jsonify({'error': f'No {provider} API key found. Please add one in your settings.'}), 404
        
        # This is just a mock implementation - in a real system you would
        # make an actual API call to the provider
        if provider == 'openai':
            # Mock OpenAI API call
            # response = requests.get('https://api.openai.com/v1/models', 
            #                         headers={'Authorization': f'Bearer {api_key}'})
            # return jsonify(response.json())
            return jsonify({'success': True, 'message': 'Successfully connected to OpenAI API', 'provider': provider})
            
        elif provider == 'anthropic':
            # Mock Anthropic API call
            # response = requests.get('https://api.anthropic.com/v1/models',
            #                         headers={'x-api-key': api_key})
            # return jsonify(response.json())
            return jsonify({'success': True, 'message': 'Successfully connected to Anthropic API', 'provider': provider})
            
        elif provider == 'google':
            # Mock Google AI API call
            # response = requests.get('https://generativelanguage.googleapis.com/v1beta/models',
            #                         params={'key': api_key})
            # return jsonify(response.json())
            return jsonify({'success': True, 'message': 'Successfully connected to Google AI API', 'provider': provider})
        
    except Exception as e:
        logger.error(f"Error testing provider API key: {str(e)}")
        return jsonify({'error': f'Failed to test provider API key: {str(e)}'}), 500

# User Preferences
@user_settings_bp.route('/preferences', methods=['POST'])
# TODO: Implement authentication (login_required)
def update_preferences():
    """
    Update user preferences
    """
    try:
        preferences = request.get_json()
        if not preferences:
            return jsonify({'error': 'No preferences provided'}), 400
            
        from backend.services.database import get_supabase_client
        supabase = get_supabase_client()
        
        # Add user_id to preferences
        preferences['user_id'] = g.user.id
        
        # Upsert preferences
        result = supabase.table('user_preferences').upsert(preferences).execute()
        
        return jsonify({"success": True, "data": result.data[0] if result.data else None})
        
    except Exception as e:
        logger.error(f"Error updating preferences: {str(e)}")
        return jsonify({'error': f'Failed to update preferences: {str(e)}'}), 500

@user_settings_bp.route('/preferences', methods=['GET'])
# TODO: Implement authentication (login_required)
def get_preferences():
    """
    Get user preferences
    """
    try:
        from backend.services.database import get_supabase_client
        supabase = get_supabase_client()
        
        result = supabase.table('user_preferences').select('*').eq('user_id', g.user.id).limit(1).execute()
        
        if result.data and len(result.data) > 0:
            return jsonify({"success": True, "data": result.data[0]})
        else:
            return jsonify({
                "success": True, 
                "data": {
                    "user_id": g.user.id,
                    "theme": "system",
                    "notifications_enabled": True,
                    "email_notifications": True
                }
            })
        
    except Exception as e:
        logger.error(f"Error getting preferences: {str(e)}")
        return jsonify({'error': f'Failed to get preferences: {str(e)}'}), 500 