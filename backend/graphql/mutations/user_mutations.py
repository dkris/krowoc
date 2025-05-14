import graphene
from backend.models import User
from backend.graphql.types import UserType, UserInput
from backend.graphql.validation import UserValidator
from backend.models.base import get_db
from pydantic import ValidationError


class CreateUser(graphene.Mutation):
    class Arguments:
        user_data = UserInput(required=True)

    user = graphene.Field(lambda: UserType)
    ok = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, user_data):
        db = get_db()
        
        # Validate input using Pydantic
        try:
            validated_data = UserValidator(
                email=user_data.email,
                display_name=user_data.display_name,
                avatar_url=user_data.avatar_url,
                is_active=user_data.is_active if user_data.is_active is not None else True
            )
        except ValidationError as e:
            return CreateUser(user=None, ok=False, message=str(e))

        # Check if user with email already exists
        existing_user = db.query(User).filter(User.email == validated_data.email).first()
        if existing_user:
            return CreateUser(
                user=None, 
                ok=False, 
                message=f"User with email {validated_data.email} already exists"
            )

        # Create new user
        user = User(
            email=validated_data.email,
            display_name=validated_data.display_name,
            avatar_url=validated_data.avatar_url,
            is_active=validated_data.is_active
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        return CreateUser(user=user, ok=True, message="User created successfully")


class UpdateUser(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        user_data = UserInput(required=True)

    user = graphene.Field(lambda: UserType)
    ok = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, id, user_data):
        db = get_db()
        
        # Find user
        user = db.query(User).filter(User.id == id).first()
        if not user:
            return UpdateUser(user=None, ok=False, message=f"User with ID {id} not found")

        # Validate input using Pydantic
        try:
            validated_data = UserValidator(
                email=user_data.email,
                display_name=user_data.display_name,
                avatar_url=user_data.avatar_url,
                is_active=user_data.is_active if user_data.is_active is not None else user.is_active
            )
        except ValidationError as e:
            return UpdateUser(user=None, ok=False, message=str(e))

        # Check if email is being changed and if it already exists
        if user.email != validated_data.email:
            existing_user = db.query(User).filter(User.email == validated_data.email).first()
            if existing_user:
                return UpdateUser(
                    user=None, 
                    ok=False, 
                    message=f"User with email {validated_data.email} already exists"
                )

        # Update user
        user.email = validated_data.email
        user.display_name = validated_data.display_name
        user.avatar_url = validated_data.avatar_url
        user.is_active = validated_data.is_active
        
        db.commit()
        db.refresh(user)
        
        return UpdateUser(user=user, ok=True, message="User updated successfully")


class DeleteUser(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, id):
        db = get_db()
        
        # Find user
        user = db.query(User).filter(User.id == id).first()
        if not user:
            return DeleteUser(ok=False, message=f"User with ID {id} not found")

        # Delete user
        db.delete(user)
        db.commit()
        
        return DeleteUser(ok=True, message="User deleted successfully")


class UserMutations(graphene.ObjectType):
    create_user = CreateUser.Field()
    update_user = UpdateUser.Field()
    delete_user = DeleteUser.Field() 