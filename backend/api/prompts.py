from flask import Blueprint, request, jsonify, Response, stream_with_context
from pydantic import ValidationError, BaseModel, Field
from backend.models import Prompt, PromptState, User
from backend.models.base import get_db
from backend.services.llm_service import llm_service, PromptRequest
from sqlalchemy.exc import SQLAlchemyError
import json
import asyncio
from functools import wraps
import traceback
from typing import List, Optional

prompt_blueprint = Blueprint('prompts', __name__, url_prefix='/api/prompts')

# Helper function to run async functions in Flask routes
def async_route(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        try:
            return loop.run_until_complete(f(*args, **kwargs))
        except Exception as e:
            traceback.print_exc()
            return jsonify({'error': str(e)}), 500
    
    return wrapper

# Pydantic models for validation
class PromptCreateModel(BaseModel):
    title: str = Field(..., min_length=3)
    description: Optional[str] = None
    prompt_text: str = Field(..., min_length=10)
    tags: Optional[List[str]] = None
    model_whitelist: Optional[List[str]] = None
    user_id: int
    state: Optional[str] = 'draft'

class PromptUpdateModel(BaseModel):
    title: str = Field(..., min_length=3)
    description: Optional[str] = None
    prompt_text: str = Field(..., min_length=10)
    tags: Optional[List[str]] = None
    model_whitelist: Optional[List[str]] = None
    user_id: int
    state: Optional[str] = None

@prompt_blueprint.route('', methods=['GET'])
def get_prompts():
    """Get all prompts with optional filtering"""
    db = next(get_db())
    query = db.query(Prompt)
    
    # Apply filters if provided
    user_id = request.args.get('user_id')
    if user_id:
        query = query.filter(Prompt.user_id == user_id)
    
    tag = request.args.get('tag')
    if tag:
        query = query.filter(Prompt.tags.contains([tag]))
    
    state = request.args.get('state')
    if state:
        try:
            state_enum = PromptState[state.upper()]
            query = query.filter(Prompt.state == state_enum)
        except KeyError:
            return jsonify({'error': f'Invalid state: {state}'}), 400
    
    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Limit pagination size
    if per_page > 100:
        per_page = 100
    
    # Execute query with pagination
    prompts_page = query.limit(per_page).offset((page - 1) * per_page).all()
    
    # Serialize response
    result = []
    for prompt in prompts_page:
        result.append({
            'id': prompt.id,
            'title': prompt.title,
            'description': prompt.description,
            'prompt_text': prompt.prompt_text,
            'tags': prompt.tags,
            'model_whitelist': prompt.model_whitelist,
            'user_id': prompt.user_id,
            'state': prompt.state.name.lower(),
            'created_at': prompt.created_at.isoformat() if prompt.created_at else None,
            'updated_at': prompt.updated_at.isoformat() if prompt.updated_at else None
        })
    
    return jsonify({
        'prompts': result,
        'page': page,
        'per_page': per_page,
        'total': query.count()
    })

@prompt_blueprint.route('/<int:prompt_id>', methods=['GET'])
def get_prompt(prompt_id):
    """Get a single prompt by ID"""
    db = next(get_db())
    prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
    
    if not prompt:
        return jsonify({'error': f'Prompt with ID {prompt_id} not found'}), 404
    
    result = {
        'id': prompt.id,
        'title': prompt.title,
        'description': prompt.description,
        'prompt_text': prompt.prompt_text,
        'tags': prompt.tags,
        'model_whitelist': prompt.model_whitelist,
        'user_id': prompt.user_id,
        'state': prompt.state.name.lower(),
        'created_at': prompt.created_at.isoformat() if prompt.created_at else None,
        'updated_at': prompt.updated_at.isoformat() if prompt.updated_at else None
    }
    
    return jsonify(result)

@prompt_blueprint.route('', methods=['POST'])
def create_prompt():
    """Create a new prompt"""
    data = request.get_json()
    db = next(get_db())
    # Validate input
    try:
        validated = PromptCreateModel(**data)
    except ValidationError as e:
        return jsonify({'error': e.errors()}), 400
    # Check if user exists
    user_id = validated.user_id
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return jsonify({'error': f'User with ID {user_id} not found'}), 404
    # Create prompt with state enum
    try:
        state_enum = PromptState[validated.state.upper()]
    except KeyError:
        return jsonify({'error': f'Invalid state: {validated.state}'}), 400
    try:
        prompt = Prompt(
            title=validated.title,
            description=validated.description,
            prompt_text=validated.prompt_text,
            tags=validated.tags,
            model_whitelist=validated.model_whitelist,
            user_id=validated.user_id,
            state=state_enum
        )
        db.add(prompt)
        db.commit()
        db.refresh(prompt)
        result = {
            'id': prompt.id,
            'title': prompt.title,
            'description': prompt.description,
            'prompt_text': prompt.prompt_text,
            'tags': prompt.tags,
            'model_whitelist': prompt.model_whitelist,
            'user_id': prompt.user_id,
            'state': prompt.state.name.lower(),
            'created_at': prompt.created_at.isoformat() if prompt.created_at else None,
            'updated_at': prompt.updated_at.isoformat() if prompt.updated_at else None
        }
        return jsonify(result), 201
    except SQLAlchemyError as e:
        db.rollback()
        return jsonify({'error': f'Database error: {str(e)}'}), 500

@prompt_blueprint.route('/<int:prompt_id>', methods=['PUT'])
def update_prompt(prompt_id):
    """Update an existing prompt"""
    data = request.get_json()
    db = next(get_db())
    # Find prompt
    prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
    if not prompt:
        return jsonify({'error': f'Prompt with ID {prompt_id} not found'}), 404
    # Validate input
    try:
        validated = PromptUpdateModel(**data)
    except ValidationError as e:
        return jsonify({'error': e.errors()}), 400
    # Check if user exists if user_id is changing
    user_id = validated.user_id
    if user_id != prompt.user_id:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return jsonify({'error': f'User with ID {user_id} not found'}), 404
    # Convert state string to enum
    state_str = validated.state or prompt.state.name.lower()
    try:
        state_enum = PromptState[state_str.upper()]
    except KeyError:
        return jsonify({'error': f'Invalid state: {state_str}'}), 400
    try:
        prompt.title = validated.title
        prompt.description = validated.description
        prompt.prompt_text = validated.prompt_text
        prompt.tags = validated.tags
        prompt.model_whitelist = validated.model_whitelist
        prompt.user_id = validated.user_id
        prompt.state = state_enum
        db.commit()
        db.refresh(prompt)
        result = {
            'id': prompt.id,
            'title': prompt.title,
            'description': prompt.description,
            'prompt_text': prompt.prompt_text,
            'tags': prompt.tags,
            'model_whitelist': prompt.model_whitelist,
            'user_id': prompt.user_id,
            'state': prompt.state.name.lower(),
            'created_at': prompt.created_at.isoformat() if prompt.created_at else None,
            'updated_at': prompt.updated_at.isoformat() if prompt.updated_at else None
        }
        return jsonify(result)
    except SQLAlchemyError as e:
        db.rollback()
        return jsonify({'error': f'Database error: {str(e)}'}), 500

@prompt_blueprint.route('/<int:prompt_id>', methods=['DELETE'])
def delete_prompt(prompt_id):
    """Delete a prompt"""
    db = next(get_db())
    
    # Find prompt
    prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
    if not prompt:
        return jsonify({'error': f'Prompt with ID {prompt_id} not found'}), 404
    
    try:
        # Delete prompt
        db.delete(prompt)
        db.commit()
        
        return jsonify({'message': f'Prompt with ID {prompt_id} deleted successfully'}), 200
    except SQLAlchemyError as e:
        db.rollback()
        return jsonify({'error': f'Database error: {str(e)}'}), 500

@prompt_blueprint.route('/<int:prompt_id>/state', methods=['PATCH'])
def update_prompt_state(prompt_id):
    """Update prompt state only"""
    data = request.get_json()
    db = next(get_db())
    
    # Validate state
    state = data.get('state')
    if not state:
        return jsonify({'error': 'State is required'}), 400
    
    try:
        state_enum = PromptState[state.upper()]
    except KeyError:
        return jsonify({'error': f'Invalid state: {state}'}), 400
    
    # Find prompt
    prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
    if not prompt:
        return jsonify({'error': f'Prompt with ID {prompt_id} not found'}), 404
    
    try:
        # Update prompt state
        prompt.state = state_enum
        db.commit()
        
        result = {
            'id': prompt.id,
            'title': prompt.title,
            'state': prompt.state.name.lower(),
            'updated_at': prompt.updated_at.isoformat() if prompt.updated_at else None
        }
        
        return jsonify(result)
    except SQLAlchemyError as e:
        db.rollback()
        return jsonify({'error': f'Database error: {str(e)}'}), 500

@prompt_blueprint.route('/<int:prompt_id>/execute', methods=['POST'])
@async_route
async def execute_prompt(prompt_id):
    """Execute a prompt with an LLM and return the result"""
    data = request.get_json()
    db = next(get_db())
    prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
    if not prompt:
        return jsonify({'error': f'Prompt with ID {prompt_id} not found'}), 404
    model = data.get('model')
    if not model:
        return jsonify({'error': 'Model must be specified'}), 400
    if prompt.model_whitelist and model not in prompt.model_whitelist:
        return jsonify({'error': f'Model {model} is not in the prompt whitelist'}), 400
    try:
        prompt_request = PromptRequest(
            prompt=prompt.prompt_text,
            model=model,
            temperature=data.get('temperature', 0.7),
            max_tokens=data.get('max_tokens', 1000),
            stream=data.get('stream', False),
            system_prompt=data.get('system_prompt'),
            tools=data.get('tools')
        )
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    if prompt_request.stream:
        return Response(
            stream_with_context(stream_llm_response(prompt_request)),
            content_type='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no'
            }
        )
    try:
        response = await llm_service.execute_prompt(prompt_request)
        return jsonify({
            'prompt_id': prompt_id,
            'model': model,
            'response': response
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@prompt_blueprint.route('/execute', methods=['POST'])
@async_route
async def execute_arbitrary_prompt():
    """Execute an arbitrary prompt with an LLM and return the result"""
    data = request.get_json()
    if 'prompt' not in data:
        return jsonify({'error': 'Prompt text must be provided'}), 400
    if 'model' not in data:
        return jsonify({'error': 'Model must be specified'}), 400
    try:
        prompt_request = PromptRequest(
            prompt=data['prompt'],
            model=data['model'],
            temperature=data.get('temperature', 0.7),
            max_tokens=data.get('max_tokens', 1000),
            stream=data.get('stream', False),
            system_prompt=data.get('system_prompt'),
            tools=data.get('tools')
        )
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    if prompt_request.stream:
        return Response(
            stream_with_context(stream_llm_response(prompt_request)),
            content_type='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no'
            }
        )
    try:
        response = await llm_service.execute_prompt(prompt_request)
        return jsonify({
            'model': data['model'],
            'response': response
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

async def stream_llm_response(prompt_request):
    """Stream the LLM response as SSE events using LangChain"""
    try:
        async for chunk in await llm_service.execute_prompt(prompt_request):
            if chunk:
                yield f"data: {json.dumps({'text': chunk})}\n\n"
        yield "event: done\ndata: null\n\n"
    except Exception as e:
        error_data = json.dumps({'error': str(e)})
        yield f"event: error\ndata: {error_data}\n\n"
        yield "event: done\ndata: null\n\n" 