from flask import Blueprint, request, jsonify
from backend.models import Execution, Prompt, User
from backend.models.base import get_db
from sqlalchemy.exc import SQLAlchemyError
import traceback
from datetime import datetime
from backend.api.auth import get_current_user_id

execution_blueprint = Blueprint('executions', __name__, url_prefix='/api/executions')

@execution_blueprint.route('', methods=['POST'])
def create_execution():
    """
    Create a new execution record
    """
    try:
        data = request.get_json()
        db = get_db()

        # Try to get current user or use the provided user_id
        try:
            user_id = get_current_user_id() or data.get('user_id')
        except:
            user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'User ID is required'}), 400

        # Check that prompt exists
        prompt_id = data.get('prompt_id')
        if not prompt_id:
            return jsonify({'error': 'Prompt ID is required'}), 400
        
        prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
        if not prompt:
            return jsonify({'error': f'Prompt with ID {prompt_id} not found'}), 404

        # Create new execution
        execution = Execution(
            prompt_id=prompt_id,
            user_id=user_id,
            model=data.get('model'),
            provider=data.get('provider'),
            input_tokens=data.get('input_tokens'),
            output_tokens=data.get('output_tokens'),
            cost=data.get('cost'),
            response_text=data.get('response_text'),
            is_successful=data.get('is_successful', True),
            error_message=data.get('error_message'),
            execution_time_ms=data.get('execution_time_ms'),
            created_at=datetime.now()
        )
        
        db.add(execution)
        db.commit()
        db.refresh(execution)
        
        return jsonify({
            'id': execution.id,
            'prompt_id': execution.prompt_id,
            'user_id': execution.user_id,
            'model': execution.model,
            'provider': execution.provider,
            'input_tokens': execution.input_tokens,
            'output_tokens': execution.output_tokens,
            'cost': execution.cost,
            'response_text': execution.response_text,
            'is_successful': execution.is_successful,
            'error_message': execution.error_message,
            'execution_time_ms': execution.execution_time_ms,
            'created_at': execution.created_at.isoformat()
        }), 201
    except SQLAlchemyError as e:
        db.rollback()
        traceback.print_exc()
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@execution_blueprint.route('/<int:execution_id>', methods=['GET'])
def get_execution(execution_id):
    """
    Get a specific execution by ID
    """
    try:
        db = get_db()
        execution = db.query(Execution).filter(Execution.id == execution_id).first()
        
        if not execution:
            return jsonify({'error': f'Execution with ID {execution_id} not found'}), 404
        
        return jsonify({
            'id': execution.id,
            'prompt_id': execution.prompt_id,
            'user_id': execution.user_id,
            'model': execution.model,
            'provider': execution.provider,
            'input_tokens': execution.input_tokens,
            'output_tokens': execution.output_tokens,
            'cost': execution.cost,
            'response_text': execution.response_text,
            'is_successful': execution.is_successful,
            'error_message': execution.error_message,
            'execution_time_ms': execution.execution_time_ms,
            'created_at': execution.created_at.isoformat()
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@execution_blueprint.route('/<int:execution_id>/retry', methods=['POST'])
def retry_execution(execution_id):
    """
    Retry a failed execution
    """
    try:
        db = get_db()
        execution = db.query(Execution).filter(Execution.id == execution_id).first()
        
        if not execution:
            return jsonify({'error': f'Execution with ID {execution_id} not found'}), 404
        
        # Create a new execution with same parameters
        new_execution = Execution(
            prompt_id=execution.prompt_id,
            user_id=execution.user_id,
            model=execution.model,
            provider=execution.provider,
            is_successful=False,  # Will be updated after execution
            created_at=datetime.now()
        )
        
        db.add(new_execution)
        db.commit()
        db.refresh(new_execution)
        
        # In a real implementation, this would call the LLM service
        # For now, we'll just return the new execution record
        return jsonify({
            'id': new_execution.id,
            'prompt_id': new_execution.prompt_id,
            'user_id': new_execution.user_id,
            'model': new_execution.model,
            'provider': new_execution.provider,
            'input_tokens': new_execution.input_tokens,
            'output_tokens': new_execution.output_tokens,
            'cost': new_execution.cost,
            'response_text': new_execution.response_text,
            'is_successful': new_execution.is_successful,
            'error_message': new_execution.error_message,
            'execution_time_ms': new_execution.execution_time_ms,
            'created_at': new_execution.created_at.isoformat()
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@execution_blueprint.route('/prompt/<int:prompt_id>', methods=['GET'])
def get_executions_by_prompt(prompt_id):
    """
    Get all executions for a specific prompt
    """
    try:
        db = get_db()
        
        # Check that prompt exists
        prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
        if not prompt:
            return jsonify({'error': f'Prompt with ID {prompt_id} not found'}), 404
        
        executions = db.query(Execution).filter(Execution.prompt_id == prompt_id).order_by(Execution.created_at.desc()).all()
        
        result = []
        for execution in executions:
            result.append({
                'id': execution.id,
                'prompt_id': execution.prompt_id,
                'user_id': execution.user_id,
                'model': execution.model,
                'provider': execution.provider,
                'input_tokens': execution.input_tokens,
                'output_tokens': execution.output_tokens,
                'cost': execution.cost,
                'response_text': execution.response_text,
                'is_successful': execution.is_successful,
                'error_message': execution.error_message,
                'execution_time_ms': execution.execution_time_ms,
                'created_at': execution.created_at.isoformat()
            })
        
        return jsonify({'executions': result})
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500 