import graphene
from graphene_sqlalchemy import SQLAlchemyConnectionField
from backend.models import User
from backend.graphql.types import UserType
from sqlalchemy.orm import joinedload


class UserQueries(graphene.ObjectType):
    node = graphene.relay.Node.Field()
    user = graphene.Field(
        UserType,
        id=graphene.Int(required=True),
        description="Get a user by ID"
    )
    users = SQLAlchemyConnectionField(
        UserType.connection,
        description="Get all users with pagination"
    )
    users_by_email = graphene.Field(
        UserType,
        email=graphene.String(required=True),
        description="Get a user by email"
    )

    def resolve_user(self, info, id):
        query = UserType.get_query(info)
        return query.filter(User.id == id).first()

    def resolve_users_by_email(self, info, email):
        query = UserType.get_query(info)
        return query.filter(User.email == email).first() 