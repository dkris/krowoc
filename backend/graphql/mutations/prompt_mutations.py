import graphene
from backend.models import Prompt, PromptState, User
from backend.graphql.types import PromptType, PromptInput
from backend.graphql.validation import PromptValidator
from backend.models.base import get_db
from pydantic import ValidationError



class CreatePrompt(graphene.Mutation):
    class Arguments:
        prompt_data = PromptInput(required=True)

    prompt = graphene.Field(lambda: PromptType)
    ok = graphene.Boolean()
    message = graphene.String()

    

    def mutate(self, info, prompt_data):
        db = get_db()
        
        # Validate input using Pydantic
        try:
            state = prompt_data.state if prompt_data.state else "draft"
            validated_data = PromptValidator(
                title=prompt_data.title,
                description=prompt_data.description,
                prompt_text=prompt_data.prompt_text,
                tags=prompt_data.tags,
                model_whitelist=prompt_data.model_whitelist,
                user_id=prompt_data.user_id,
                state=state
            )
        except ValidationError as e:
            return CreatePrompt(prompt=None, ok=False, message=str(e))

        # Check if user exists
        user = db.query(User).filter(User.id == validated_data.user_id).first()
        if not user:
            return CreatePrompt(
                prompt=None, 
                ok=False, 
                message=f"User with ID {validated_data.user_id} not found"
            )

        # Create prompt state enum
        state_enum = PromptState[validated_data.state.upper()]

        # Create new prompt
        prompt = Prompt(
            title=validated_data.title,
            description=validated_data.description,
            prompt_text=validated_data.prompt_text,
            tags=validated_data.tags,
            model_whitelist=validated_data.model_whitelist,
            user_id=validated_data.user_id,
            state=state_enum
        )
        
        db.add(prompt)
        db.commit()
        db.refresh(prompt)
        
        return CreatePrompt(prompt=prompt, ok=True, message="Prompt created successfully")


class UpdatePrompt(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        prompt_data = PromptInput(required=True)

    prompt = graphene.Field(lambda: PromptType)
    ok = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, id, prompt_data):
        db = get_db()
        
        # Find prompt
        prompt = db.query(Prompt).filter(Prompt.id == id).first()
        if not prompt:
            return UpdatePrompt(prompt=None, ok=False, message=f"Prompt with ID {id} not found")

        # Validate input using Pydantic
        try:
            state = prompt_data.state if prompt_data.state else prompt.state.name.lower()
            validated_data = PromptValidator(
                title=prompt_data.title,
                description=prompt_data.description,
                prompt_text=prompt_data.prompt_text,
                tags=prompt_data.tags if prompt_data.tags is not None else prompt.tags,
                model_whitelist=prompt_data.model_whitelist if prompt_data.model_whitelist is not None else prompt.model_whitelist,
                user_id=prompt_data.user_id,
                state=state
            )
        except ValidationError as e:
            return UpdatePrompt(prompt=None, ok=False, message=str(e))

        # Check if user exists
        user = db.query(User).filter(User.id == validated_data.user_id).first()
        if not user:
            return UpdatePrompt(
                prompt=None, 
                ok=False, 
                message=f"User with ID {validated_data.user_id} not found"
            )

        # Create prompt state enum
        state_enum = PromptState[validated_data.state.upper()]

        # Update prompt
        prompt.title = validated_data.title
        prompt.description = validated_data.description
        prompt.prompt_text = validated_data.prompt_text
        prompt.tags = validated_data.tags
        prompt.model_whitelist = validated_data.model_whitelist
        prompt.user_id = validated_data.user_id
        prompt.state = state_enum
        
        db.commit()
        db.refresh(prompt)
        
        return UpdatePrompt(prompt=prompt, ok=True, message="Prompt updated successfully")


class DeletePrompt(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, id):
        db = get_db()
        
        # Find prompt
        prompt = db.query(Prompt).filter(Prompt.id == id).first()
        if not prompt:
            return DeletePrompt(ok=False, message=f"Prompt with ID {id} not found")

        # Delete prompt
        db.delete(prompt)
        db.commit()
        
        return DeletePrompt(ok=True, message="Prompt deleted successfully")


class PromptMutations(graphene.ObjectType):
    create_prompt = CreatePrompt.Field()
    update_prompt = UpdatePrompt.Field()
    delete_prompt = DeletePrompt.Field() 