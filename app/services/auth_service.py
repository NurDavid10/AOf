"""
Authentication and authorization service.

This module handles user authentication, password hashing, and session management.
"""

import bcrypt
from typing import Optional
from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from app.database import get_db_context


class AuthService:
    """
    Service class for authentication and authorization operations.

    Provides methods for:
    - Password hashing and verification
    - User authentication
    - Role-based access control
    """

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using bcrypt.

        Args:
            password: Plain text password to hash

        Returns:
            str: Hashed password

        Raises:
            ValueError: If password is empty or invalid

        Example:
            hashed = AuthService.hash_password("password123")
        """
        try:
            if not password or len(password) < 1:
                raise ValueError("Password cannot be empty")

            # Generate salt and hash password
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
            return hashed.decode('utf-8')

        except Exception as e:
            raise ValueError(f"Error hashing password: {str(e)}")

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash.

        Args:
            plain_password: Plain text password to verify
            hashed_password: Hashed password to compare against

        Returns:
            bool: True if password matches, False otherwise

        Example:
            is_valid = AuthService.verify_password("password123", hashed)
        """
        try:
            return bcrypt.checkpw(
                plain_password.encode('utf-8'),
                hashed_password.encode('utf-8')
            )
        except Exception as e:
            print(f"Error verifying password: {str(e)}")
            return False

    @staticmethod
    def authenticate_user(username: str, password: str, db: Session) -> Optional[User]:
        """
        Authenticate a user with username and password.

        Args:
            username: User's username
            password: User's plain text password
            db: Database session

        Returns:
            Optional[User]: User object if authentication successful, None otherwise

        Example:
            user = AuthService.authenticate_user("john", "password123", db)
            if user:
                print(f"Welcome {user.full_name}!")
        """
        try:
            # Query user by username
            user = db.query(User).filter(User.username == username).first()

            if not user:
                return None

            # Verify password
            if not AuthService.verify_password(password, user.password_hash):
                return None

            # Check if user is active
            if not user.is_active:
                return None

            return user

        except Exception as e:
            print(f"Error authenticating user: {str(e)}")
            return None

    @staticmethod
    def get_user_by_id(user_id: int, db: Session) -> Optional[User]:
        """
        Get user by ID.

        Args:
            user_id: User's ID
            db: Database session

        Returns:
            Optional[User]: User object if found, None otherwise
        """
        try:
            return db.query(User).filter(User.id == user_id).first()
        except Exception as e:
            print(f"Error getting user by ID: {str(e)}")
            return None

    @staticmethod
    def get_user_by_username(username: str, db: Session) -> Optional[User]:
        """
        Get user by username.

        Args:
            username: User's username
            db: Database session

        Returns:
            Optional[User]: User object if found, None otherwise
        """
        try:
            return db.query(User).filter(User.username == username).first()
        except Exception as e:
            print(f"Error getting user by username: {str(e)}")
            return None

    @staticmethod
    def check_permission(user: User, permission: str) -> bool:
        """
        Check if user has a specific permission.

        Args:
            user: User object
            permission: Permission string to check

        Returns:
            bool: True if user has permission, False otherwise

        Example:
            if AuthService.check_permission(user, "manage_courses"):
                # Allow access
        """
        try:
            return user.can_access(permission)
        except Exception as e:
            print(f"Error checking permission: {str(e)}")
            return False

    @staticmethod
    def is_role(user: User, role: UserRole) -> bool:
        """
        Check if user has a specific role.

        Args:
            user: User object
            role: UserRole enum value

        Returns:
            bool: True if user has the role, False otherwise

        Example:
            if AuthService.is_role(user, UserRole.MANAGER):
                # Show manager features
        """
        try:
            return user.role == role
        except Exception as e:
            print(f"Error checking role: {str(e)}")
            return False

    @staticmethod
    def get_dashboard_route(user: User) -> str:
        """
        Get the dashboard route for a user based on their role.

        Args:
            user: User object

        Returns:
            str: Dashboard route path

        Example:
            route = AuthService.get_dashboard_route(user)
            # Returns "/manager/dashboard" for managers
        """
        try:
            return user.get_dashboard_route()
        except Exception as e:
            print(f"Error getting dashboard route: {str(e)}")
            return "/login"
