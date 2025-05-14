import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType
from backend.models import User


class UserType(SQLAlchemyObjectType):
    """GraphQL type for User model"""
    class Meta:
        model = User
        exclude_fields = ('api_keys',)  # Exclude sensitive fields
        interfaces = (graphene.relay.Node,)


class UserInput(graphene.InputObjectType):
    """Input type for User mutations"""
    email = graphene.String(required=True)
    display_name = graphene.String(required=False)
    avatar_url = graphene.String(required=False)
    is_active = graphene.Boolean(required=False) 