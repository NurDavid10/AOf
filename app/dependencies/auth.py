"""
Authentication dependencies for FastAPI routes.

This module provides dependency functions for authentication and authorization.
"""

from fastapi import Request, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.auth_service import AuthService
from app.models.user import User


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    """
    Get the currently logged-in user from the session.

    Args:
        request: FastAPI request object
        db: Database session

    Returns:
        User: Current user object

    Raises:
        HTTPException: If user is not logged in
    """
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user = AuthService.get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user


