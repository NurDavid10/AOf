"""
Demo user seeding service.

This module handles automatic creation of demo users on application startup.
"""

from datetime import date, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from app.services.user_service import UserService
from app.database import get_db_context


def create_demo_users(db: Session) -> None:
    """
    Create demo users if they don't exist in the database.
    
    This function checks for the existence of the following demo users:
    - manager1 / password123 (role: Manager)
    - teacher1 / password123 (role: Teacher)
    - student1 / password123 (role: Student)
    - parent1  / password123 (role: Parent)
    - worker1  / password123 (role: Worker)
    
    If any of these users don't exist, they are created with appropriate
    role-specific profiles.
    
    Args:
        db: Database session
    """
    demo_users = [
        {
            "username": "manager1",
            "password": "password123",
            "email": "manager1@academic.com",
            "full_name": "Alice Manager",
            "role": UserRole.MANAGER,
            "profile_data": {
                "department": "Administration",
                "access_level": 10
            }
        },
        {
            "username": "teacher1",
            "password": "password123",
            "email": "teacher1@academic.com",
            "full_name": "Carol Math",
            "role": UserRole.TEACHER,
            "profile_data": {
                "subject_specialization": "Mathematics",
                "hire_date": date.today() - timedelta(days=365),
                "salary": Decimal("50000.00")
            }
        },
        {
            "username": "student1",
            "password": "password123",
            "email": "student1@academic.com",
            "full_name": "Harry Potter",
            "role": UserRole.STUDENT,
            "profile_data": {
                "enrollment_date": date.today() - timedelta(days=30),
                "grade_level": "Grade 10",
                "parent_id": None
            }
        },
        {
            "username": "parent1",
            "password": "password123",
            "email": "parent1@academic.com",
            "full_name": "James Potter Sr",
            "role": UserRole.PARENT,
            "profile_data": {
                "phone_number": "+1-555-0100",
                "address": "100 Main Street, City, State"
            }
        },
        {
            "username": "worker1",
            "password": "password123",
            "email": "worker1@academic.com",
            "full_name": "Argus Filch",
            "role": UserRole.WORKER,
            "profile_data": {
                "job_title": "Maintenance",
                "hire_date": date.today() - timedelta(days=730),
                "hourly_rate": Decimal("25.00")
            }
        }
    ]
    
    created_count = 0
    skipped_count = 0
    
    for user_data in demo_users:
        # Check if user already exists
        existing_user = db.query(User).filter(User.username == user_data["username"]).first()
        
        if existing_user:
            skipped_count += 1
            continue
        
        # Create user with profile
        user, error = UserService.create_user_with_profile(
            username=user_data["username"],
            password=user_data["password"],
            email=user_data["email"],
            full_name=user_data["full_name"],
            role=user_data["role"],
            profile_data=user_data["profile_data"],
            db=db
        )
        
        if error:
            print(f"Warning: Failed to create demo user '{user_data['username']}': {error}")
        else:
            created_count += 1
    
    if created_count > 0:
        print(f"✓ Created {created_count} demo user(s) on startup")
    if skipped_count > 0:
        print(f"✓ Skipped {skipped_count} existing demo user(s)")


def init_demo_users() -> None:
    """
    Initialize demo users on application startup.
    
    This function should be called during application startup to ensure
    demo users exist in the database.
    """
    try:
        with get_db_context() as db:
            create_demo_users(db)
    except Exception as e:
        print(f"Warning: Failed to initialize demo users: {str(e)}")

