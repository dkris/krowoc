import graphene
from graphene_sqlalchemy import SQLAlchemyConnectionField
from backend.models import Prompt, PromptState
from backend.graphql.types import PromptType


class PromptQueries(graphene.ObjectType):
    node = graphene.relay.Node.Field()
    prompt = graphene.Field(
        PromptType,
        id=graphene.Int(required=True),
        description="Get a prompt by ID"
    )
    prompts = SQLAlchemyConnectionField(
        PromptType.connection,
        description="Get all prompts with pagination"
    )
    prompts_by_user = graphene.List(
        PromptType,
        user_id=graphene.Int(required=True),
        description="Get all prompts for a specific user"
    )
    prompts_by_tag = graphene.List(
        PromptType,
        tag=graphene.String(required=True),
        description="Get all prompts with a specific tag"
    )
    prompts_by_state = graphene.List(
        PromptType,
        state=graphene.String(required=True),
        description="Get all prompts in a specific state"
    )

    def resolve_prompt(self, info, id):
        query = PromptType.get_query(info)
        return query.filter(Prompt.id == id).first()

    def resolve_prompts_by_user(self, info, user_id):
        query = PromptType.get_query(info)
        return query.filter(Prompt.user_id == user_id).all()

    def resolve_prompts_by_tag(self, info, tag):
        query = PromptType.get_query(info)
        return query.filter(Prompt.tags.contains([tag])).all()

    def resolve_prompts_by_state(self, info, state):
        query = PromptType.get_query(info)
        try:
            state_enum = PromptState[state.upper()]
            return query.filter(Prompt.state == state_enum).all()
        except KeyError:
            return [] 