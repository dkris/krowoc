import os
from supabase import create_client, Client
from jose import jwt
from typing import Optional, Dict, Any
from loguru import logger
from flask import request, current_app
from ..models import User
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

class AuthService:
    def __init__(self, db_session: Session):
        self.db_session = db_session
        supabase_url = os.environ.get("SUPABASE_URL")
        supabase_key = os.environ.get("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            logger.warning("Supabase credentials not set in environment variables")
            self.supabase = None
        else:
            self.supabase: Client = create_client(supabase_url, supabase_key)
    
    def get_current_user(self) -> Optional[User]:
        """
        Extract JWT token from request, validate it and return the corresponding user
        """
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None
        
        token = auth_header.replace("Bearer ", "")
        try:
            # Verify token with Supabase's JWT signature
            jwt_secret = os.environ.get("SUPABASE_JWT_SECRET")
            if not jwt_secret:
                logger.error("SUPABASE_JWT_SECRET not set in environment variables")
                return None
                
            payload = jwt.decode(
                token, 
                jwt_secret, 
                algorithms=["HS256"],
                options={"verify_aud": False}
            )
            
            sub = payload.get("sub")
            if not sub:
                logger.error("No subject claim in JWT token")
                return None
                
            # Get user from database or create if not exists
            user = self._get_or_create_user(sub, payload)
            return user
            
        except jwt.JWTError as e:
            logger.error(f"JWT validation error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return None
    
    def _get_or_create_user(self, auth_id: str, claims: Dict[Any, Any]) -> Optional[User]:
        """
        Get user from database or create a new one based on JWT claims
        """
        try:
            # Try to find user by auth_id
            user = self.db_session.query(User).filter(User.auth_id == auth_id).first()
            
            if user:
                return user
                
            # If user doesn't exist, create a new one
            email = claims.get("email", "")
            name = claims.get("name", "")
            
            if not email:
                logger.error("No email in JWT claims")
                return None
                
            new_user = User(
                email=email,
                display_name=name,
                auth_provider="supabase",
                auth_id=auth_id,
                is_active=True
            )
            
            self.db_session.add(new_user)
            self.db_session.commit()
            logger.info(f"Created new user: {new_user.email}")
            
            return new_user
            
        except SQLAlchemyError as e:
            self.db_session.rollback()
            logger.error(f"Database error in user creation: {str(e)}")
            return None 