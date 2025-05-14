import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType
from backend.models import ApiKey


class ApiKeyType(SQLAlchemyObjectType):
    """GraphQL type for ApiKey model"""
    class Meta:
        model = ApiKey
        # Exclude the key_hash field for security
        exclude_fields = ('key_hash',)
        interfaces = (graphene.relay.Node,)


class ApiKeyInput(graphene.InputObjectType):
    """Input type for ApiKey mutations"""
    user_id = graphene.Int(required=True)
    provider = graphene.String(required=True)
    key = graphene.String(required=True, description="The API key (will be hashed)")
    is_active = graphene.Boolean(required=False) 