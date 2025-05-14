import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyEnumType
from backend.models import Prompt, PromptState


class PromptStateEnum(SQLAlchemyEnumType):
    """GraphQL enum type for PromptState"""
    class Meta:
        model = PromptState


class PromptType(SQLAlchemyObjectType):
    """GraphQL type for Prompt model"""
    class Meta:
        model = Prompt
        interfaces = (graphene.relay.Node,)
    
    state = graphene.Field(PromptStateEnum)


class PromptInput(graphene.InputObjectType):
    """Input type for Prompt mutations"""
    title = graphene.String(required=True)
    description = graphene.String(required=False)
    prompt_text = graphene.String(required=True)
    tags = graphene.List(graphene.String, required=False)
    model_whitelist = graphene.List(graphene.String, required=False)
    user_id = graphene.Int(required=True)
    state = graphene.String(required=False) 