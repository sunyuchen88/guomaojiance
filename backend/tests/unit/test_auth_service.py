import pytest
from datetime import datetime, timedelta
from app.services.auth_service import AuthService
from app.models.user import User
from app.utils.security import get_password_hash, verify_password, decode_access_token


@pytest.mark.unit
def test_verify_credentials_success(db, test_user):
    """Test successful credential verification"""
    auth_service = AuthService(db)
    user = auth_service.verify_credentials("testuser", "testpass123")

    assert user is not None
    assert user.username == "testuser"
    assert user.role == "inspector"


@pytest.mark.unit
def test_verify_credentials_wrong_password(db, test_user):
    """Test credential verification with wrong password"""
    auth_service = AuthService(db)
    user = auth_service.verify_credentials("testuser", "wrongpassword")

    assert user is None


@pytest.mark.unit
def test_verify_credentials_nonexistent_user(db):
    """Test credential verification with non-existent user"""
    auth_service = AuthService(db)
    user = auth_service.verify_credentials("nonexistent", "password123")

    assert user is None


@pytest.mark.unit
def test_create_access_token(db):
    """Test JWT token creation"""
    auth_service = AuthService(db)
    token = auth_service.create_access_token(username="testuser")

    assert token is not None
    assert isinstance(token, str)

    # Verify token can be decoded
    payload = decode_access_token(token)
    assert payload is not None
    assert payload["sub"] == "testuser"
    assert "exp" in payload


@pytest.mark.unit
def test_update_last_login(db, test_user):
    """Test updating last login timestamp"""
    auth_service = AuthService(db)

    # Get initial last_login_at
    initial_last_login = test_user.last_login_at

    # Update last login
    auth_service.update_last_login(test_user)
    db.refresh(test_user)

    # Verify it was updated
    assert test_user.last_login_at is not None
    if initial_last_login:
        assert test_user.last_login_at > initial_last_login
