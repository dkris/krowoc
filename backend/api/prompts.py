from flask import Blueprint, request, jsonify, Response, stream_with_context
from pydantic import ValidationError
from backend.models import Prompt, PromptState, User
from backend.models.base import get_db
from backend.graphql.validation.models import PromptValidator
from backend.services.llm_service import llm_service, PromptRequest
from sqlalchemy.exc import SQLAlchemyError
import json
import asyncio
from functools import wraps
import traceback

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

@prompt_blueprint.route('', methods=['GET'])
def get_prompts():
    """Get all prompts with optional filtering"""
    db = get_db()
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
    db = get_db()
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
    db = get_db()
    
    # Validate input
    try:
        # Set default state if not provided
        state = data.get('state', 'draft')
        validated_data = PromptValidator(
            title=data.get('title'),
            description=data.get('description'),
            prompt_text=data.get('prompt_text'),
            tags=data.get('tags'),
            model_whitelist=data.get('model_whitelist'),
            user_id=data.get('user_id'),
            state=state
        )
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    
    # Check if user exists
    user = db.query(User).filter(User.id == validated_data.user_id).first()
    if not user:
        return jsonify({'error': f'User with ID {validated_data.user_id} not found'}), 404
    
    # Create prompt with state enum
    state_enum = PromptState[validated_data.state.upper()]
    
    try:
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
    db = get_db()
    
    # Find prompt
    prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
    if not prompt:
        return jsonify({'error': f'Prompt with ID {prompt_id} not found'}), 404
    
    # Validate input
    try:
        # Use existing values for optional fields if not provided
        state = data.get('state', prompt.state.name.lower())
        validated_data = PromptValidator(
            title=data.get('title', prompt.title),
            description=data.get('description', prompt.description),
            prompt_text=data.get('prompt_text', prompt.prompt_text),
            tags=data.get('tags', prompt.tags),
            model_whitelist=data.get('model_whitelist', prompt.model_whitelist),
            user_id=data.get('user_id', prompt.user_id),
            state=state
        )
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    
    # Check if user exists if user_id is changing
    if validated_data.user_id != prompt.user_id:
        user = db.query(User).filter(User.id == validated_data.user_id).first()
        if not user:
            return jsonify({'error': f'User with ID {validated_data.user_id} not found'}), 404
    
    # Convert state string to enum
    state_enum = PromptState[validated_data.state.upper()]
    
    try:
        # Update prompt fields
        prompt.title = validated_data.title
        prompt.description = validated_data.description
        prompt.prompt_text = validated_data.prompt_text
        prompt.tags = validated_data.tags
        prompt.model_whitelist = validated_data.model_whitelist
        prompt.user_id = validated_data.user_id
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
    db = get_db()
    
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
    db = get_db()
    
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
    db = get_db()
    
    # Get the prompt from the database
    prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
    if not prompt:
        return jsonify({'error': f'Prompt with ID {prompt_id} not found'}), 404
    
    # Get execution parameters
    model = data.get('model')
    if not model:
        return jsonify({'error': 'Model must be specified'}), 400
    
    # Check if model is in the prompt's whitelist (if any)
    if prompt.model_whitelist and model not in prompt.model_whitelist:
        return jsonify({'error': f'Model {model} is not in the prompt whitelist'}), 400
    
    # Prepare prompt request
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
    
    # Handle streaming response
    if prompt_request.stream:
        return Response(
            stream_with_context(stream_llm_response(prompt_request)),
            content_type='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no'
            }
        )
    
    # Handle regular response
    try:
        response = await llm_service.execute_prompt(prompt_request)
        return jsonify({
            'prompt_id': prompt_id,
            'model': model,
            'response': response.text,
            'usage': response.usage,
            'finish_reason': response.finish_reason
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@prompt_blueprint.route('/execute', methods=['POST'])
@async_route
async def execute_arbitrary_prompt():
    """Execute an arbitrary prompt with an LLM and return the result"""
    data = request.get_json()
    
    # Validate input
    if 'prompt' not in data:
        return jsonify({'error': 'Prompt text must be provided'}), 400
    
    if 'model' not in data:
        return jsonify({'error': 'Model must be specified'}), 400
    
    # Prepare prompt request
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
    
    # Handle streaming response
    if prompt_request.stream:
        return Response(
            stream_with_context(stream_llm_response(prompt_request)),
            content_type='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no'
            }
        )
    
    # Handle regular response
    try:
        response = await llm_service.execute_prompt(prompt_request)
        return jsonify({
            'model': data['model'],
            'response': response.text,
            'usage': response.usage,
            'finish_reason': response.finish_reason
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

async def stream_llm_response(prompt_request):
    """Stream the LLM response as SSE events"""
    try:
        async for chunk in await llm_service.execute_prompt(prompt_request):
            if chunk.text:
                yield f"data: {json.dumps({'text': chunk.text})}\n\n"
            
            # If this is the last chunk, send finish info
            if chunk.is_last:
                yield f"data: {json.dumps({'finish_reason': chunk.finish_reason, 'usage': chunk.usage})}\n\n"
                yield "event: done\ndata: null\n\n"
    except Exception as e:
        error_data = json.dumps({'error': str(e)})
        yield f"event: error\ndata: {error_data}\n\n"
        yield "event: done\ndata: null\n\n" 