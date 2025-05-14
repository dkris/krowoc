import graphene
from backend.models import Execution, Prompt, User
from backend.graphql.types import ExecutionType, ExecutionInput
from backend.graphql.validation import ExecutionValidator
from backend.models.base import get_db
from pydantic import ValidationError


class CreateExecution(graphene.Mutation):
    class Arguments:
        execution_data = ExecutionInput(required=True)

    execution = graphene.Field(lambda: ExecutionType)
    ok = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, execution_data):
        db = get_db()
        
        # Validate input using Pydantic
        try:
            validated_data = ExecutionValidator(
                prompt_id=execution_data.prompt_id,
                user_id=execution_data.user_id,
                model=execution_data.model,
                provider=execution_data.provider,
                input_tokens=execution_data.input_tokens,
                output_tokens=execution_data.output_tokens,
                cost=execution_data.cost,
                response_text=execution_data.response_text,
                is_successful=execution_data.is_successful if execution_data.is_successful is not None else True,
                error_message=execution_data.error_message,
                execution_time_ms=execution_data.execution_time_ms
            )
        except ValidationError as e:
            return CreateExecution(execution=None, ok=False, message=str(e))

        # Check if prompt exists
        prompt = db.query(Prompt).filter(Prompt.id == validated_data.prompt_id).first()
        if not prompt:
            return CreateExecution(
                execution=None, 
                ok=False, 
                message=f"Prompt with ID {validated_data.prompt_id} not found"
            )

        # Check if user exists
        user = db.query(User).filter(User.id == validated_data.user_id).first()
        if not user:
            return CreateExecution(
                execution=None, 
                ok=False, 
                message=f"User with ID {validated_data.user_id} not found"
            )

        # Create new execution
        execution = Execution(
            prompt_id=validated_data.prompt_id,
            user_id=validated_data.user_id,
            model=validated_data.model,
            provider=validated_data.provider,
            input_tokens=validated_data.input_tokens,
            output_tokens=validated_data.output_tokens,
            cost=validated_data.cost,
            response_text=validated_data.response_text,
            is_successful=validated_data.is_successful,
            error_message=validated_data.error_message,
            execution_time_ms=validated_data.execution_time_ms
        )
        
        db.add(execution)
        db.commit()
        db.refresh(execution)
        
        return CreateExecution(execution=execution, ok=True, message="Execution created successfully")


class UpdateExecution(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        execution_data = ExecutionInput(required=True)

    execution = graphene.Field(lambda: ExecutionType)
    ok = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, id, execution_data):
        db = get_db()
        
        # Find execution
        execution = db.query(Execution).filter(Execution.id == id).first()
        if not execution:
            return UpdateExecution(execution=None, ok=False, message=f"Execution with ID {id} not found")

        # Validate input using Pydantic
        try:
            validated_data = ExecutionValidator(
                prompt_id=execution_data.prompt_id,
                user_id=execution_data.user_id,
                model=execution_data.model,
                provider=execution_data.provider,
                input_tokens=execution_data.input_tokens,
                output_tokens=execution_data.output_tokens,
                cost=execution_data.cost,
                response_text=execution_data.response_text,
                is_successful=execution_data.is_successful if execution_data.is_successful is not None else execution.is_successful,
                error_message=execution_data.error_message,
                execution_time_ms=execution_data.execution_time_ms
            )
        except ValidationError as e:
            return UpdateExecution(execution=None, ok=False, message=str(e))

        # Check if prompt exists
        prompt = db.query(Prompt).filter(Prompt.id == validated_data.prompt_id).first()
        if not prompt:
            return UpdateExecution(
                execution=None, 
                ok=False, 
                message=f"Prompt with ID {validated_data.prompt_id} not found"
            )

        # Check if user exists
        user = db.query(User).filter(User.id == validated_data.user_id).first()
        if not user:
            return UpdateExecution(
                execution=None, 
                ok=False, 
                message=f"User with ID {validated_data.user_id} not found"
            )

        # Update execution
        execution.prompt_id = validated_data.prompt_id
        execution.user_id = validated_data.user_id
        execution.model = validated_data.model
        execution.provider = validated_data.provider
        execution.input_tokens = validated_data.input_tokens
        execution.output_tokens = validated_data.output_tokens
        execution.cost = validated_data.cost
        execution.response_text = validated_data.response_text
        execution.is_successful = validated_data.is_successful
        execution.error_message = validated_data.error_message
        execution.execution_time_ms = validated_data.execution_time_ms
        
        db.commit()
        db.refresh(execution)
        
        return UpdateExecution(execution=execution, ok=True, message="Execution updated successfully")


class DeleteExecution(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, id):
        db = get_db()
        
        # Find execution
        execution = db.query(Execution).filter(Execution.id == id).first()
        if not execution:
            return DeleteExecution(ok=False, message=f"Execution with ID {id} not found")

        # Delete execution
        db.delete(execution)
        db.commit()
        
        return DeleteExecution(ok=True, message="Execution deleted successfully")


class ExecutionMutations(graphene.ObjectType):
    create_execution = CreateExecution.Field()
    update_execution = UpdateExecution.Field()
    delete_execution = DeleteExecution.Field() 