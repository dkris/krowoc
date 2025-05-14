import graphene
from backend.graphql.queries import (
    UserQueries,
    PromptQueries,
    ExecutionQueries,
    ApiKeyQueries
)
from backend.graphql.mutations import (
    UserMutations,
    PromptMutations,
    ExecutionMutations,
    ApiKeyMutations
)


class Query(
    UserQueries,
    PromptQueries,
    ExecutionQueries,
    ApiKeyQueries,
    graphene.ObjectType
):
    """Root GraphQL Query"""
    pass


class Mutation(
    UserMutations,
    PromptMutations,
    ExecutionMutations,
    ApiKeyMutations,
    graphene.ObjectType
):
    """Root GraphQL Mutation"""
    pass


schema = graphene.Schema(query=Query, mutation=Mutation) 