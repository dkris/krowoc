import logging
from backend.services.database import get_supabase_client
from backend.services.auth import verify_password

logger = logging.getLogger(__name__)

async def get_provider_api_key(user_id, provider):
    """
    Securely retrieve a provider API key.
    This function only returns the raw key when needed for making API calls,
    and should be called only at the point when the key is needed.
    """
    try:
        supabase = get_supabase_client()
        
        # Get the key from the database
        result = supabase.table('provider_api_keys').select(
            'key_hash'
        ).eq('user_id', user_id).eq('provider', provider).execute()
        
        if not result.data or len(result.data) == 0:
            logger.warning(f"No API key found for user {user_id} and provider {provider}")
            return None
            
        key_hash = result.data[0]['key_hash']
        
        # TODO: In a real implementation, we would decrypt the key here
        # This is a placeholder for a proper key retrieval mechanism
        # DO NOT implement like this in production - this is unsafe!
        # Instead, use a secure method to store and retrieve keys (e.g., AWS KMS, Vault)
        
        return "PLACEHOLDER_KEY_VALUE"
        
    except Exception as e:
        logger.error(f"Error retrieving provider API key: {str(e)}")
        return None

async def verify_provider_api_key(user_id, provider, api_key):
    """
    Verify a provider API key against the stored hash.
    This is useful when a client needs to verify they have the correct key.
    """
    try:
        supabase = get_supabase_client()
        
        # Get the key hash from the database
        result = supabase.table('provider_api_keys').select(
            'key_hash'
        ).eq('user_id', user_id).eq('provider', provider).execute()
        
        if not result.data or len(result.data) == 0:
            logger.warning(f"No API key found for user {user_id} and provider {provider}")
            return False
            
        key_hash = result.data[0]['key_hash']
        
        # Verify the key against the hash
        is_valid = verify_password(api_key, key_hash)
        
        # Update last used timestamp if key is valid
        if is_valid:
            from datetime import datetime, timezone
            current_time = datetime.now(timezone.utc)
            supabase.table('provider_api_keys').update({
                'last_used_at': current_time.isoformat()
            }).eq('user_id', user_id).eq('provider', provider).execute()
        
        return is_valid
        
    except Exception as e:
        logger.error(f"Error verifying provider API key: {str(e)}")
        return False 