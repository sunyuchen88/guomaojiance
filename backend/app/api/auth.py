from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.user import UserLogin, TokenResponse, UserResponse
from app.services.auth_service import AuthService
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
def login(
    credentials: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Login endpoint to authenticate users and return JWT token.

    Args:
        credentials: User login credentials (username and password)
        db: Database session

    Returns:
        TokenResponse with access_token and user information

    Raises:
        HTTPException 401: If credentials are invalid
    """
    auth_service = AuthService(db)

    # Attempt login
    result = auth_service.login(credentials.username, credentials.password)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Convert User model to UserResponse schema
    user_response = UserResponse.from_orm(result["user"])

    return TokenResponse(
        access_token=result["access_token"],
        token_type="bearer",
        user=user_response
    )


@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(current_user: User = Depends(get_current_user)):
    """
    Logout endpoint (client-side token removal).

    Note: JWT tokens are stateless, so logout is handled on client-side
    by removing the token from storage. This endpoint exists for
    consistency and potential future server-side logout logic.

    Args:
        current_user: The authenticated user

    Returns:
        Success message
    """
    return {"message": "Successfully logged out"}
