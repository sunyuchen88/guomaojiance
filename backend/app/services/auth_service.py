from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.models.user import User
from app.utils.security import verify_password, create_access_token


class AuthService:
    """Authentication service for user login and token management"""

    def __init__(self, db: Session):
        self.db = db

    def verify_credentials(self, username: str, password: str) -> Optional[User]:
        """
        Verify user credentials.

        Args:
            username: The username to verify
            password: The plain text password to verify

        Returns:
            The User object if credentials are valid, None otherwise
        """
        # Query user by username
        user = self.db.query(User).filter(User.username == username).first()

        if not user:
            return None

        # Verify password
        if not verify_password(password, user.password_hash):
            return None

        return user

    def create_access_token(self, username: str) -> str:
        """
        Create a JWT access token for the user.

        Args:
            username: The username to encode in the token

        Returns:
            The JWT access token
        """
        data = {"sub": username}
        return create_access_token(data)

    def update_last_login(self, user: User) -> None:
        """
        Update the user's last login timestamp.

        Args:
            user: The User object to update
        """
        user.last_login_at = datetime.utcnow()
        self.db.commit()

    def login(self, username: str, password: str) -> Optional[dict]:
        """
        Perform complete login flow: verify credentials, create token, update last login.

        Args:
            username: The username
            password: The plain text password

        Returns:
            A dictionary with 'user' and 'access_token' if successful, None otherwise
        """
        # Verify credentials
        user = self.verify_credentials(username, password)

        if not user:
            return None

        # Update last login
        self.update_last_login(user)

        # Create access token
        access_token = self.create_access_token(username)

        return {
            "user": user,
            "access_token": access_token
        }
