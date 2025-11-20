import pytest
from fastapi.testclient import TestClient


@pytest.mark.contract
def test_login_success(client: TestClient, test_user):
    """Test successful login with valid credentials"""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "testuser", "password": "testpass123"}
    )

    assert response.status_code == 200
    data = response.json()

    # Verify response structure
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer"
    assert "user" in data

    # Verify user data
    user_data = data["user"]
    assert user_data["username"] == "testuser"
    assert user_data["name"] == "Test User"
    assert user_data["role"] == "inspector"
    assert "id" in user_data
    assert "created_at" in user_data


@pytest.mark.contract
def test_login_invalid_credentials(client: TestClient, test_user):
    """Test login with invalid password"""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "testuser", "password": "wrongpassword"}
    )

    assert response.status_code == 401
    assert "detail" in response.json()


@pytest.mark.contract
def test_login_nonexistent_user(client: TestClient):
    """Test login with non-existent username"""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "nonexistent", "password": "password123"}
    )

    assert response.status_code == 401


@pytest.mark.contract
def test_login_missing_username(client: TestClient):
    """Test login with missing username field"""
    response = client.post(
        "/api/v1/auth/login",
        json={"password": "testpass123"}
    )

    assert response.status_code == 422  # Validation error


@pytest.mark.contract
def test_login_missing_password(client: TestClient):
    """Test login with missing password field"""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "testuser"}
    )

    assert response.status_code == 422  # Validation error


@pytest.mark.contract
def test_login_short_password(client: TestClient):
    """Test login with password shorter than 8 characters"""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "testuser", "password": "short"}
    )

    assert response.status_code == 422  # Validation error
