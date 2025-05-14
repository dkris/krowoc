import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType
from backend.models import Execution


class ExecutionType(SQLAlchemyObjectType):
    """GraphQL type for Execution model"""
    class Meta:
        model = Execution
        interfaces = (graphene.relay.Node,)


class ExecutionInput(graphene.InputObjectType):
    """Input type for Execution mutations"""
    prompt_id = graphene.Int(required=True)
    user_id = graphene.Int(required=True)
    model = graphene.String(required=True)
    provider = graphene.String(required=True)
    input_tokens = graphene.Int(required=False)
    output_tokens = graphene.Int(required=False)
    cost = graphene.Float(required=False)
    response_text = graphene.String(required=False)
    is_successful = graphene.Boolean(required=False)
    error_message = graphene.String(required=False)
    execution_time_ms = graphene.Int(required=False) 