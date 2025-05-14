import graphene
from graphene_sqlalchemy import SQLAlchemyConnectionField
from backend.models import ApiKey
from backend.graphql.types import ApiKeyType


class ApiKeyQueries(graphene.ObjectType):
    node = graphene.relay.Node.Field()
    api_key = graphene.Field(
        ApiKeyType,
        id=graphene.Int(required=True),
        description="Get an API key by ID"
    )
    api_keys_by_user = graphene.List(
        ApiKeyType,
        user_id=graphene.Int(required=True),
        description="Get all API keys for a specific user"
    )
    api_keys_by_provider = graphene.List(
        ApiKeyType,
        user_id=graphene.Int(required=True),
        provider=graphene.String(required=True),
        description="Get all API keys for a specific user and provider"
    )

    def resolve_api_key(self, info, id):
        query = ApiKeyType.get_query(info)
        return query.filter(ApiKey.id == id).first()

    def resolve_api_keys_by_user(self, info, user_id):
        query = ApiKeyType.get_query(info)
        return query.filter(ApiKey.user_id == user_id).all()

    def resolve_api_keys_by_provider(self, info, user_id, provider):
        query = ApiKeyType.get_query(info)
        return query.filter(
            ApiKey.user_id == user_id,
            ApiKey.provider == provider
        ).all() 