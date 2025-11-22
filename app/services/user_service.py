"""
User management service.

This module handles user CRUD operations and validations,
including unique username validation as required.
"""

from typing import List, Optional
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.user import User, Manager, Teacher, Student, Parent, Worker, UserRole
from app.services.auth_service import AuthService


class UserService:
    """
    Service class for user management operations.

    Provides methods for:
    - User creation with unique username validation
    - User profile management
    - Role-specific operations
    """

    @staticmethod
    def validate_unique_username(username: str, db: Session) -> bool:
        """
        Validate that username is unique (REQUIRED VALIDATION).

        Args:
            username: Username to validate
            db: Database session

        Returns:
            bool: True if username is unique, False otherwise

        Example:
            if UserService.validate_unique_username("john123", db):
                # Username is available
        """
        try:
            existing_user = db.query(User).filter(User.username == username).first()
            return existing_user is None
        except Exception as e:
            print(f"Error validating username: {str(e)}")
            return False

    @staticmethod
    def create_user(
        username: str,
        password: str,
        email: str,
        full_name: str,
        role: UserRole,
        db: Session
    ) -> tuple[Optional[User], Optional[str]]:
        """
        Create a new user with validation.

        Args:
            username: Unique username
            password: Plain text password
            email: User's email
            full_name: User's full name
            role: User's role
            db: Database session

        Returns:
            tuple: (User object or None, error message or None)

        Example:
            user, error = UserService.create_user(
                "john123", "password", "john@example.com",
                "John Doe", UserRole.STUDENT, db
            )
            if error:
                print(f"Error: {error}")
        """
        try:
            # Validate unique username (REQUIRED)
            if not UserService.validate_unique_username(username, db):
                return None, "Username already exists. Please choose a different username."

            # Hash password
            password_hash = AuthService.hash_password(password)

            # Create user
            user = User(
                username=username,
                password_hash=password_hash,
                email=email,
                full_name=full_name,
                role=role
            )

            db.add(user)
            db.commit()
            db.refresh(user)

            return user, None

        except IntegrityError as e:
            db.rollback()
            return None, "Database constraint violation. Username or email may already exist."
        except Exception as e:
            db.rollback()
            return None, f"Error creating user: {str(e)}"

    @staticmethod
    def create_manager_profile(
        user_id: int,
        department: Optional[str],
        access_level: int,
        db: Session
    ) -> tuple[Optional[Manager], Optional[str]]:
        """
        Create a manager profile for a user.

        Args:
            user_id: User's ID
            department: Manager's department
            access_level: Access level (1-10)
            db: Database session

        Returns:
            tuple: (Manager object or None, error message or None)
        """
        try:
            manager = Manager(
                user_id=user_id,
                department=department,
                access_level=access_level
            )

            db.add(manager)
            db.commit()
            db.refresh(manager)

            return manager, None

        except IntegrityError:
            db.rollback()
            return None, "Manager profile already exists for this user."
        except Exception as e:
            db.rollback()
            return None, f"Error creating manager profile: {str(e)}"

    @staticmethod
    def get_all_users(db: Session) -> List[User]:
        """
        Get all users.

        Args:
            db: Database session

        Returns:
            List[User]: List of all users
        """
        try:
            return db.query(User).all()
        except Exception as e:
            print(f"Error getting all users: {str(e)}")
            return []

    @staticmethod
    def get_users_by_role(role: UserRole, db: Session) -> List[User]:
        """
        Get all users with a specific role.

        Args:
            role: User role to filter by
            db: Database session

        Returns:
            List[User]: List of users with the specified role
        """
        try:
            return db.query(User).filter(User.role == role).all()
        except Exception as e:
            print(f"Error getting users by role: {str(e)}")
            return []

    @staticmethod
    def update_user(
        user_id: int,
        email: Optional[str] = None,
        full_name: Optional[str] = None,
        db: Session = None
    ) -> tuple[Optional[User], Optional[str]]:
        """
        Update user information.

        Args:
            user_id: User's ID
            email: New email (optional)
            full_name: New full name (optional)
            db: Database session

        Returns:
            tuple: (Updated User object or None, error message or None)
        """
        try:
            user = db.query(User).filter(User.id == user_id).first()

            if not user:
                return None, "User not found"

            if email:
                user.email = email
            if full_name:
                user.full_name = full_name

            db.commit()
            db.refresh(user)

            return user, None

        except Exception as e:
            db.rollback()
            return None, f"Error updating user: {str(e)}"

    @staticmethod
    def delete_user(user_id: int, db: Session) -> tuple[bool, Optional[str]]:
        """
        Delete a user.

        Args:
            user_id: User's ID
            db: Database session

        Returns:
            tuple: (Success boolean, error message or None)
        """
        try:
            user = db.query(User).filter(User.id == user_id).first()

            if not user:
                return False, "User not found"

            db.delete(user)
            db.commit()

            return True, None

        except Exception as e:
            db.rollback()
            return False, f"Error deleting user: {str(e)}"

    @staticmethod
    def create_teacher_profile(
        user_id: int,
        subject_specialization: Optional[str],
        hire_date: Optional[date],
        salary: Optional[Decimal],
        db: Session
    ) -> tuple[Optional[Teacher], Optional[str]]:
        """
        Create a teacher profile for a user.

        Args:
            user_id: User's ID
            subject_specialization: Teacher's subject specialization
            hire_date: Date of hire
            salary: Teacher's salary
            db: Database session

        Returns:
            tuple: (Teacher object or None, error message or None)
        """
        try:
            teacher = Teacher(
                user_id=user_id,
                subject_specialization=subject_specialization,
                hire_date=hire_date,
                salary=salary
            )

            db.add(teacher)
            db.commit()
            db.refresh(teacher)

            return teacher, None

        except IntegrityError:
            db.rollback()
            return None, "Teacher profile already exists for this user."
        except Exception as e:
            db.rollback()
            return None, f"Error creating teacher profile: {str(e)}"

    @staticmethod
    def create_student_profile(
        user_id: int,
        enrollment_date: Optional[date],
        grade_level: Optional[str],
        parent_id: Optional[int],
        db: Session
    ) -> tuple[Optional[Student], Optional[str]]:
        """
        Create a student profile for a user.

        Args:
            user_id: User's ID
            enrollment_date: Date of enrollment
            grade_level: Student's grade level
            parent_id: Parent's user ID (optional)
            db: Database session

        Returns:
            tuple: (Student object or None, error message or None)
        """
        try:
            # Validate parent exists if provided
            if parent_id:
                parent = db.query(Parent).filter(Parent.user_id == parent_id).first()
                if not parent:
                    return None, "Parent not found."

            student = Student(
                user_id=user_id,
                enrollment_date=enrollment_date,
                grade_level=grade_level,
                parent_id=parent_id
            )

            db.add(student)
            db.commit()
            db.refresh(student)

            return student, None

        except IntegrityError:
            db.rollback()
            return None, "Student profile already exists for this user."
        except Exception as e:
            db.rollback()
            return None, f"Error creating student profile: {str(e)}"

    @staticmethod
    def create_parent_profile(
        user_id: int,
        phone_number: Optional[str],
        address: Optional[str],
        db: Session
    ) -> tuple[Optional[Parent], Optional[str]]:
        """
        Create a parent profile for a user.

        Args:
            user_id: User's ID
            phone_number: Parent's phone number
            address: Parent's address
            db: Database session

        Returns:
            tuple: (Parent object or None, error message or None)
        """
        try:
            parent = Parent(
                user_id=user_id,
                phone_number=phone_number,
                address=address
            )

            db.add(parent)
            db.commit()
            db.refresh(parent)

            return parent, None

        except IntegrityError:
            db.rollback()
            return None, "Parent profile already exists for this user."
        except Exception as e:
            db.rollback()
            return None, f"Error creating parent profile: {str(e)}"

    @staticmethod
    def create_worker_profile(
        user_id: int,
        job_title: Optional[str],
        hire_date: Optional[date],
        hourly_rate: Optional[Decimal],
        db: Session
    ) -> tuple[Optional[Worker], Optional[str]]:
        """
        Create a worker profile for a user.

        Args:
            user_id: User's ID
            job_title: Worker's job title
            hire_date: Date of hire
            hourly_rate: Worker's hourly rate
            db: Database session

        Returns:
            tuple: (Worker object or None, error message or None)
        """
        try:
            worker = Worker(
                user_id=user_id,
                job_title=job_title,
                hire_date=hire_date,
                hourly_rate=hourly_rate
            )

            db.add(worker)
            db.commit()
            db.refresh(worker)

            return worker, None

        except IntegrityError:
            db.rollback()
            return None, "Worker profile already exists for this user."
        except Exception as e:
            db.rollback()
            return None, f"Error creating worker profile: {str(e)}"

    @staticmethod
    def create_user_with_profile(
        username: str,
        password: str,
        email: str,
        full_name: str,
        role: UserRole,
        profile_data: dict,
        db: Session
    ) -> tuple[Optional[User], Optional[str]]:
        """
        Create a user and their role-specific profile in one transaction.

        Args:
            username: Unique username
            password: Plain text password
            email: User's email
            full_name: User's full name
            role: User's role
            profile_data: Dictionary containing role-specific profile data
            db: Database session

        Returns:
            tuple: (User object or None, error message or None)

        Example:
            user, error = UserService.create_user_with_profile(
                "teacher1", "pass", "teacher@example.com", "John Teacher",
                UserRole.TEACHER,
                {
                    "subject_specialization": "Math",
                    "hire_date": date.today(),
                    "salary": Decimal("50000.00")
                },
                db
            )
        """
        try:
            # Create base user
            user, error = UserService.create_user(
                username, password, email, full_name, role, db
            )

            if error:
                return None, error

            # Create role-specific profile
            profile_error = None
            if role == UserRole.MANAGER:
                _, profile_error = UserService.create_manager_profile(
                    user.id,
                    profile_data.get('department'),
                    profile_data.get('access_level', 1),
                    db
                )
            elif role == UserRole.TEACHER:
                _, profile_error = UserService.create_teacher_profile(
                    user.id,
                    profile_data.get('subject_specialization'),
                    profile_data.get('hire_date'),
                    profile_data.get('salary'),
                    db
                )
            elif role == UserRole.STUDENT:
                _, profile_error = UserService.create_student_profile(
                    user.id,
                    profile_data.get('enrollment_date'),
                    profile_data.get('grade_level'),
                    profile_data.get('parent_id'),
                    db
                )
            elif role == UserRole.PARENT:
                _, profile_error = UserService.create_parent_profile(
                    user.id,
                    profile_data.get('phone_number'),
                    profile_data.get('address'),
                    db
                )
            elif role == UserRole.WORKER:
                _, profile_error = UserService.create_worker_profile(
                    user.id,
                    profile_data.get('job_title'),
                    profile_data.get('hire_date'),
                    profile_data.get('hourly_rate'),
                    db
                )

            if profile_error:
                # Rollback user creation if profile fails
                db.delete(user)
                db.commit()
                return None, profile_error

            return user, None

        except Exception as e:
            db.rollback()
            return None, f"Error creating user with profile: {str(e)}"

    @staticmethod
    def get_parent_children(parent_id: int, db: Session) -> List[Student]:
        """
        Get all children for a parent.

        Args:
            parent_id: Parent's user ID
            db: Database session

        Returns:
            List[Student]: List of student children
        """
        try:
            return db.query(Student).filter(Student.parent_id == parent_id).all()
        except Exception as e:
            print(f"Error getting parent children: {str(e)}")
            return []
