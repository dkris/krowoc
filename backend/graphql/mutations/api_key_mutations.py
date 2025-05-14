import graphene
import hashlib
from backend.models import ApiKey, User
from backend.graphql.types import ApiKeyType, ApiKeyInput
from backend.graphql.validation import ApiKeyValidator
from backend.models.base import get_db
from pydantic import ValidationError


def hash_api_key(key):
    """Hash API key for secure storage"""
    return hashlib.sha256(key.encode()).hexdigest()


class CreateApiKey(graphene.Mutation):
    class Arguments:
        api_key_data = ApiKeyInput(required=True)

    api_key = graphene.Field(lambda: ApiKeyType)
    ok = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, api_key_data):
        db = get_db()
        
        # Validate input using Pydantic
        try:
            validated_data = ApiKeyValidator(
                user_id=api_key_data.user_id,
                provider=api_key_data.provider,
                key=api_key_data.key,
                is_active=api_key_data.is_active if api_key_data.is_active is not None else True
            )
        except ValidationError as e:
            return CreateApiKey(api_key=None, ok=False, message=str(e))

        # Check if user exists
        user = db.query(User).filter(User.id == validated_data.user_id).first()
        if not user:
            return CreateApiKey(
                api_key=None, 
                ok=False, 
                message=f"User with ID {validated_data.user_id} not found"
            )

        # Check if key for this provider already exists for this user
        existing_key = db.query(ApiKey).filter(
            ApiKey.user_id == validated_data.user_id,
            ApiKey.provider == validated_data.provider
        ).first()
        
        if existing_key:
            return CreateApiKey(
                api_key=None, 
                ok=False, 
                message=f"API key for provider {validated_data.provider} already exists for this user"
            )

        # Hash the API key
        key_hash = hash_api_key(validated_data.key)

        # Create new API key
        api_key = ApiKey(
            user_id=validated_data.user_id,
            provider=validated_data.provider,
            key_hash=key_hash,
            is_active=validated_data.is_active
        )
        
        db.add(api_key)
        db.commit()
        db.refresh(api_key)
        
        return CreateApiKey(api_key=api_key, ok=True, message="API key created successfully")


class UpdateApiKey(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        api_key_data = ApiKeyInput(required=True)

    api_key = graphene.Field(lambda: ApiKeyType)
    ok = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, id, api_key_data):
        db = get_db()
        
        # Find API key
        api_key = db.query(ApiKey).filter(ApiKey.id == id).first()
        if not api_key:
            return UpdateApiKey(api_key=None, ok=False, message=f"API key with ID {id} not found")

        # Validate input using Pydantic
        try:
            validated_data = ApiKeyValidator(
                user_id=api_key_data.user_id,
                provider=api_key_data.provider,
                key=api_key_data.key,
                is_active=api_key_data.is_active if api_key_data.is_active is not None else api_key.is_active
            )
        except ValidationError as e:
            return UpdateApiKey(api_key=None, ok=False, message=str(e))

        # Check if user exists
        user = db.query(User).filter(User.id == validated_data.user_id).first()
        if not user:
            return UpdateApiKey(
                api_key=None, 
                ok=False, 
                message=f"User with ID {validated_data.user_id} not found"
            )

        # If provider is being changed, check if key for new provider already exists
        if api_key.provider != validated_data.provider:
            existing_key = db.query(ApiKey).filter(
                ApiKey.user_id == validated_data.user_id,
                ApiKey.provider == validated_data.provider
            ).first()
            
            if existing_key:
                return UpdateApiKey(
                    api_key=None, 
                    ok=False, 
                    message=f"API key for provider {validated_data.provider} already exists for this user"
                )

        # Hash the API key
        key_hash = hash_api_key(validated_data.key)

        # Update API key
        api_key.user_id = validated_data.user_id
        api_key.provider = validated_data.provider
        api_key.key_hash = key_hash
        api_key.is_active = validated_data.is_active
        
        db.commit()
        db.refresh(api_key)
        
        return UpdateApiKey(api_key=api_key, ok=True, message="API key updated successfully")


class DeleteApiKey(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, id):
        db = get_db()
        
        # Find API key
        api_key = db.query(ApiKey).filter(ApiKey.id == id).first()
        if not api_key:
            return DeleteApiKey(ok=False, message=f"API key with ID {id} not found")

        # Delete API key
        db.delete(api_key)
        db.commit()
        
        return DeleteApiKey(ok=True, message="API key deleted successfully")


class ApiKeyMutations(graphene.ObjectType):
    create_api_key = CreateApiKey.Field()
    update_api_key = UpdateApiKey.Field()
    delete_api_key = DeleteApiKey.Field() 