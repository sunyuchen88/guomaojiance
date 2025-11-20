import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.models.user import User
from app.utils.security import get_password_hash

# Create in-memory SQLite database for testing
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """
    Create a fresh database for each test function.
    """
    # Create tables
    Base.metadata.create_all(bind=engine)

    # Create session
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """
    Create a test client with a test database session.
    """

    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_user(db):
    """
    Create a test user in the database.
    """
    user = User(
        username="testuser",
        password_hash=get_password_hash("testpass123"),
        name="Test User",
        role="inspector",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture(scope="function")
def test_admin(db):
    """
    Create a test admin user in the database.
    """
    admin = User(
        username="testadmin",
        password_hash=get_password_hash("adminpass123"),
        name="Test Admin",
        role="admin",
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin


@pytest.fixture(scope="function")
def auth_headers(client, test_user):
    """
    Get authentication headers for a test user.
    """
    # Login to get token
    response = client.post(
        "/api/v1/auth/login", json={"username": "testuser", "password": "testpass123"}
    )
    token = response.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
def admin_headers(client, test_admin):
    """
    Get authentication headers for a test admin.
    """
    # Login to get token
    response = client.post(
        "/api/v1/auth/login", json={"username": "testadmin", "password": "adminpass123"}
    )
    token = response.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}
