import pytest
import os
from unittest.mock import patch, MagicMock
from backend.services.auth_service import AuthService
from backend.models.user import User

@pytest.fixture
def mock_db_session():
    session = MagicMock()
    query = MagicMock()
    session.query.return_value = query
    filter_query = MagicMock()
    query.filter.return_value = filter_query
    filter_query.first.return_value = None
    return session

def test_get_or_create_user_existing_user(mock_db_session):
    # Setup
    user = User(id=1, email="test@example.com", display_name="Test User", auth_provider="supabase", auth_id="123456")
    query = mock_db_session.query.return_value
    filter_query = query.filter.return_value
    filter_query.first.return_value = user
    
    auth_service = AuthService(mock_db_session)
    
    # Execute
    claims = {"email": "test@example.com", "name": "Test User"}
    result = auth_service._get_or_create_user("123456", claims)
    
    # Assert
    assert result == user
    mock_db_session.add.assert_not_called()
    mock_db_session.commit.assert_not_called()

def test_get_or_create_user_new_user(mock_db_session):
    # Setup
    auth_service = AuthService(mock_db_session)
    
    # Execute
    claims = {"email": "new@example.com", "name": "New User"}
    result = auth_service._get_or_create_user("new_auth_id", claims)
    
    # Assert
    assert result is not None
    assert result.email == "new@example.com"
    assert result.display_name == "New User"
    assert result.auth_provider == "supabase"
    assert result.auth_id == "new_auth_id"
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()

def test_get_or_create_user_missing_email(mock_db_session):
    # Setup
    auth_service = AuthService(mock_db_session)
    
    # Execute
    claims = {"name": "New User"}  # Missing email
    result = auth_service._get_or_create_user("new_auth_id", claims)
    
    # Assert
    assert result is None
    mock_db_session.add.assert_not_called()
    mock_db_session.commit.assert_not_called()

@patch('os.environ.get')
def test_init_with_missing_credentials(mock_env_get, mock_db_session):
    # Setup
    mock_env_get.return_value = None
    
    # Execute
    auth_service = AuthService(mock_db_session)
    
    # Assert
    assert auth_service.supabase is None 