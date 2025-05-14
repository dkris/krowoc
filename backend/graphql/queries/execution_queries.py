import graphene
from graphene_sqlalchemy import SQLAlchemyConnectionField
from backend.models import Execution
from backend.graphql.types import ExecutionType


class ExecutionQueries(graphene.ObjectType):
    node = graphene.relay.Node.Field()
    execution = graphene.Field(
        ExecutionType,
        id=graphene.Int(required=True),
        description="Get an execution by ID"
    )
    executions = SQLAlchemyConnectionField(
        ExecutionType.connection,
        description="Get all executions with pagination"
    )
    executions_by_user = graphene.List(
        ExecutionType,
        user_id=graphene.Int(required=True),
        description="Get all executions for a specific user"
    )
    executions_by_prompt = graphene.List(
        ExecutionType,
        prompt_id=graphene.Int(required=True),
        description="Get all executions for a specific prompt"
    )
    executions_by_model = graphene.List(
        ExecutionType,
        model=graphene.String(required=True),
        description="Get all executions for a specific model"
    )

    def resolve_execution(self, info, id):
        query = ExecutionType.get_query(info)
        return query.filter(Execution.id == id).first()

    def resolve_executions_by_user(self, info, user_id):
        query = ExecutionType.get_query(info)
        return query.filter(Execution.user_id == user_id).all()

    def resolve_executions_by_prompt(self, info, prompt_id):
        query = ExecutionType.get_query(info)
        return query.filter(Execution.prompt_id == prompt_id).all()

    def resolve_executions_by_model(self, info, model):
        query = ExecutionType.get_query(info)
        return query.filter(Execution.model == model).all() 