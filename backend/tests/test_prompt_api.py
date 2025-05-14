import pytest
import json
from backend.app import create_app
from backend.models import User, Prompt, PromptState
from backend.models.base import get_db

@pytest.fixture
def app():
    app = create_app({
        'TESTING': True,
        'DATABASE_URL': 'sqlite:///:memory:'
    })
    
    # Create tables
    from backend.models.base import Base, engine
    Base.metadata.create_all(bind=engine)
    
    # Create test data
    with app.app_context():
        db = get_db()
        
        # Create a test user
        user = User(
            email='test@example.com',
            display_name='Test User'
        )
        db.add(user)
        db.commit()
        
        # Create test prompts
        prompts = [
            Prompt(
                title='Test Prompt 1',
                description='Description for test prompt 1',
                prompt_text='This is test prompt 1',
                tags=['test', 'prompt'],
                model_whitelist=['gpt-3.5-turbo', 'gpt-4'],
                user_id=user.id,
                state=PromptState.DRAFT
            ),
            Prompt(
                title='Test Prompt 2',
                description='Description for test prompt 2',
                prompt_text='This is test prompt 2',
                tags=['test', 'another'],
                model_whitelist=['gpt-4'],
                user_id=user.id,
                state=PromptState.PUBLISHED
            ),
            Prompt(
                title='Test Prompt 3',
                description='Description for test prompt 3',
                prompt_text='This is test prompt 3',
                tags=['archived'],
                model_whitelist=['gpt-3.5-turbo'],
                user_id=user.id,
                state=PromptState.ARCHIVED
            )
        ]
        
        for prompt in prompts:
            db.add(prompt)
        
        db.commit()
    
    yield app
    
    # Clean up
    with app.app_context():
        db = get_db()
        db.execute('DROP TABLE IF EXISTS prompts')
        db.execute('DROP TABLE IF EXISTS users')
        db.commit()

@pytest.fixture
def client(app):
    return app.test_client()


def test_get_prompts(client):
    """Test getting all prompts"""
    response = client.get('/api/prompts')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert 'prompts' in data
    assert len(data['prompts']) == 3
    assert data['prompts'][0]['title'] == 'Test Prompt 1'


def test_get_prompt_by_id(client):
    """Test getting a single prompt by ID"""
    # First get all prompts to find the ID
    response = client.get('/api/prompts')
    prompts = json.loads(response.data)['prompts']
    prompt_id = prompts[0]['id']
    
    # Now get the specific prompt
    response = client.get(f'/api/prompts/{prompt_id}')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['id'] == prompt_id
    assert data['title'] == 'Test Prompt 1'
    assert data['state'] == 'draft'


def test_create_prompt(client, app):
    """Test creating a new prompt"""
    with app.app_context():
        db = get_db()
        user = db.query(User).first()
    
    new_prompt = {
        'title': 'New Test Prompt',
        'description': 'Description for new test prompt',
        'prompt_text': 'This is a new test prompt',
        'tags': ['new', 'test'],
        'model_whitelist': ['gpt-3.5-turbo'],
        'user_id': user.id,
        'state': 'draft'
    }
    
    response = client.post(
        '/api/prompts',
        data=json.dumps(new_prompt),
        content_type='application/json'
    )
    
    assert response.status_code == 201
    
    data = json.loads(response.data)
    assert data['title'] == 'New Test Prompt'
    assert data['state'] == 'draft'
    
    # Verify it was added to the database
    response = client.get('/api/prompts')
    prompts = json.loads(response.data)['prompts']
    assert len(prompts) == 4


def test_update_prompt(client, app):
    """Test updating an existing prompt"""
    # First get all prompts to find the ID
    response = client.get('/api/prompts')
    prompts = json.loads(response.data)['prompts']
    prompt_id = prompts[0]['id']
    
    with app.app_context():
        db = get_db()
        user = db.query(User).first()
    
    updated_data = {
        'title': 'Updated Prompt Title',
        'description': 'Updated description',
        'prompt_text': 'This is the updated prompt text',
        'tags': ['updated', 'test'],
        'model_whitelist': ['gpt-4'],
        'user_id': user.id,
        'state': 'published'
    }
    
    response = client.put(
        f'/api/prompts/{prompt_id}',
        data=json.dumps(updated_data),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['title'] == 'Updated Prompt Title'
    assert data['state'] == 'published'
    
    # Verify it was updated in the database
    response = client.get(f'/api/prompts/{prompt_id}')
    updated_prompt = json.loads(response.data)
    assert updated_prompt['title'] == 'Updated Prompt Title'
    assert updated_prompt['state'] == 'published'


def test_delete_prompt(client):
    """Test deleting a prompt"""
    # First get all prompts to find the ID
    response = client.get('/api/prompts')
    prompts = json.loads(response.data)['prompts']
    prompt_id = prompts[0]['id']
    initial_count = len(prompts)
    
    # Delete the prompt
    response = client.delete(f'/api/prompts/{prompt_id}')
    assert response.status_code == 200
    
    # Verify it was deleted
    response = client.get('/api/prompts')
    prompts = json.loads(response.data)['prompts']
    assert len(prompts) == initial_count - 1
    
    # Verify we get a 404 when trying to fetch the deleted prompt
    response = client.get(f'/api/prompts/{prompt_id}')
    assert response.status_code == 404


def test_update_prompt_state(client):
    """Test updating just the prompt state"""
    # First get all prompts to find the ID
    response = client.get('/api/prompts')
    prompts = json.loads(response.data)['prompts']
    prompt_id = prompts[0]['id']
    
    # Update the state
    response = client.patch(
        f'/api/prompts/{prompt_id}/state',
        data=json.dumps({'state': 'archived'}),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['state'] == 'archived'
    
    # Verify it was updated in the database
    response = client.get(f'/api/prompts/{prompt_id}')
    updated_prompt = json.loads(response.data)
    assert updated_prompt['state'] == 'archived'


def test_filter_prompts_by_state(client):
    """Test filtering prompts by state"""
    response = client.get('/api/prompts?state=published')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert len(data['prompts']) == 1
    assert data['prompts'][0]['state'] == 'published'


def test_filter_prompts_by_tag(client):
    """Test filtering prompts by tag"""
    response = client.get('/api/prompts?tag=archived')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert len(data['prompts']) == 1
    assert 'archived' in data['prompts'][0]['tags']


def test_prompt_validation(client, app):
    """Test prompt validation"""
    with app.app_context():
        db = get_db()
        user = db.query(User).first()
    
    # Test missing required fields
    invalid_prompt = {
        'description': 'Missing required fields',
        'user_id': user.id
    }
    
    response = client.post(
        '/api/prompts',
        data=json.dumps(invalid_prompt),
        content_type='application/json'
    )
    
    assert response.status_code == 400
    
    # Test too short title
    invalid_prompt = {
        'title': 'AB',  # Too short
        'prompt_text': 'This is a test prompt',
        'user_id': user.id
    }
    
    response = client.post(
        '/api/prompts',
        data=json.dumps(invalid_prompt),
        content_type='application/json'
    )
    
    assert response.status_code == 400
    
    # Test too short prompt text
    invalid_prompt = {
        'title': 'Valid Title',
        'prompt_text': 'Too short',  # Less than 10 chars
        'user_id': user.id
    }
    
    response = client.post(
        '/api/prompts',
        data=json.dumps(invalid_prompt),
        content_type='application/json'
    )
    
    assert response.status_code == 400
    
    # Test invalid state
    invalid_prompt = {
        'title': 'Valid Title',
        'prompt_text': 'This is a valid prompt text',
        'user_id': user.id,
        'state': 'invalid_state'  # Invalid state
    }
    
    response = client.post(
        '/api/prompts',
        data=json.dumps(invalid_prompt),
        content_type='application/json'
    )
    
    assert response.status_code == 400 