"""
User models implementing OOP inheritance hierarchy.

This module demonstrates:
- Inheritance: Base User class extended by role-specific classes
- Polymorphism: Overridden methods for role-specific behavior
- Encapsulation: Properties with getters/setters for data access
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Date, Enum, DECIMAL
from sqlalchemy.orm import relationship
import enum
from decimal import Decimal
from app.models.base import BaseModel


class UserRole(str, enum.Enum):
    """Enumeration of user roles in the system."""
    MANAGER = "manager"
    TEACHER = "teacher"
    STUDENT = "student"
    PARENT = "parent"
    WORKER = "worker"


class User(BaseModel):
    """
    Base User class demonstrating OOP inheritance.

    This is the parent class for all user types in the system.
    It provides common functionality that all users share.

    Attributes:
        username: Unique username for login
        password_hash: Hashed password for security
        email: User's email address
        full_name: User's full name
        role: User's role in the system
    """

    __tablename__ = "users"

    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(100), unique=True, index=True)
    full_name = Column(String(100))
    role = Column(Enum(UserRole), nullable=False)

    # Encapsulation: Private attribute with getter/setter
    _is_active = Column("is_active", Integer, default=1)

    @property
    def is_active(self) -> bool:
        """
        Get user active status.

        Returns:
            bool: True if user is active, False otherwise
        """
        return bool(self._is_active)

    @is_active.setter
    def is_active(self, value: bool):
        """
        Set user active status.

        Args:
            value: Boolean indicating if user should be active
        """
        self._is_active = 1 if value else 0

    def get_dashboard_route(self) -> str:
        """
        Get the dashboard route for this user (Polymorphism).

        Returns:
            str: The route path to the user's dashboard

        Note:
            This method can be overridden by derived classes
            to provide role-specific behavior.
        """
        return f"/{self.role.value}/dashboard"

    def get_permissions(self) -> list[str]:
        """
        Get list of permissions for this user (Polymorphism).

        Returns:
            list[str]: List of permission strings

        Note:
            This method should be overridden by derived classes
            to provide role-specific permissions.
        """
        return ["view_profile"]

    def can_access(self, resource: str) -> bool:
        """
        Check if user can access a resource (Polymorphism).

        Args:
            resource: Resource name to check access for

        Returns:
            bool: True if user can access the resource, False otherwise
        """
        return resource in self.get_permissions()

    def __repr__(self) -> str:
        """String representation of User."""
        return f"<User(id={self.id}, username='{self.username}', role='{self.role.value}')>"


class Manager(BaseModel):
    """
    Manager user class demonstrating inheritance and polymorphism.

    Managers have full access to the system and can manage all entities.
    """

    __tablename__ = "managers"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    department = Column(String(100))
    access_level = Column(Integer, default=1)

    # Relationship to User
    user = relationship("User", backref="manager_profile", foreign_keys=[user_id])

    @property
    def username(self) -> str:
        """Get username from associated User."""
        return self.user.username if self.user else ""

    @property
    def full_name(self) -> str:
        """Get full name from associated User."""
        return self.user.full_name if self.user else ""

    def get_permissions(self) -> list[str]:
        """
        Override: Managers have full permissions.

        Returns:
            list[str]: List of all available permissions
        """
        return [
            "view_profile", "edit_profile",
            "manage_users", "manage_courses", "manage_tasks",
            "manage_payments", "manage_queues",
            "view_reports", "view_analytics"
        ]

    def can_manage_user(self, user_role: UserRole) -> bool:
        """
        Check if manager can manage users of a specific role.

        Args:
            user_role: The role to check management permission for

        Returns:
            bool: True if manager can manage users of this role
        """
        return self.access_level >= 1

    def __repr__(self) -> str:
        """String representation of Manager."""
        return f"<Manager(user_id={self.user_id}, department='{self.department}')>"


class Teacher(BaseModel):
    """
    Teacher user class demonstrating inheritance and polymorphism.

    Teachers can manage courses, create tasks, and grade students.
    """

    __tablename__ = "teachers"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    subject_specialization = Column(String(100))
    hire_date = Column(Date)
    salary = Column(DECIMAL(10, 2))

    # Relationship to User
    user = relationship("User", backref="teacher_profile", foreign_keys=[user_id])

    # Encapsulation: Private salary attribute with getter/setter
    @property
    def salary_amount(self) -> Decimal:
        """
        Get teacher's salary.

        Returns:
            Decimal: Salary amount
        """
        return self.salary if self.salary else Decimal("0.00")

    @salary_amount.setter
    def salary_amount(self, value: Decimal):
        """
        Set teacher's salary.

        Args:
            value: New salary amount
        """
        self.salary = value

    @property
    def username(self) -> str:
        """Get username from associated User."""
        return self.user.username if self.user else ""

    @property
    def full_name(self) -> str:
        """Get full name from associated User."""
        return self.user.full_name if self.user else ""

    def get_permissions(self) -> list[str]:
        """
        Override: Teachers have course and grading permissions.

        Returns:
            list[str]: List of teacher-specific permissions
        """
        return [
            "view_profile", "edit_profile",
            "view_my_courses", "manage_my_tasks",
            "grade_students", "view_my_students"
        ]

    def can_grade_student(self, student_id: int) -> bool:
        """
        Check if teacher can grade a specific student.

        Args:
            student_id: ID of the student

        Returns:
            bool: True if teacher can grade this student

        Note:
            This should check if student is enrolled in teacher's course
        """
        # This would need to check course enrollments
        return True

    def __repr__(self) -> str:
        """String representation of Teacher."""
        return f"<Teacher(user_id={self.user_id}, subject='{self.subject_specialization}')>"


class Student(BaseModel):
    """
    Student user class demonstrating inheritance and polymorphism.

    Students can view courses, submit tasks, and view grades.
    """

    __tablename__ = "students"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    enrollment_date = Column(Date)
    grade_level = Column(String(20))
    parent_id = Column(Integer, ForeignKey("parents.user_id", ondelete="SET NULL"), nullable=True)

    # Relationships
    user = relationship("User", backref="student_profile", foreign_keys=[user_id])
    parent = relationship("Parent", backref="children", foreign_keys=[parent_id])

    @property
    def username(self) -> str:
        """Get username from associated User."""
        return self.user.username if self.user else ""

    @property
    def full_name(self) -> str:
        """Get full name from associated User."""
        return self.user.full_name if self.user else ""

    @property
    def has_parent(self) -> bool:
        """
        Check if student has an associated parent.

        Returns:
            bool: True if student has a parent, False otherwise
        """
        return self.parent_id is not None

    def get_permissions(self) -> list[str]:
        """
        Override: Students have viewing and submission permissions.

        Returns:
            list[str]: List of student-specific permissions
        """
        return [
            "view_profile", "edit_profile",
            "view_my_courses", "view_my_tasks",
            "submit_tasks", "view_my_grades",
            "view_my_payments", "join_queues"
        ]

    def can_enroll_in_course(self, course_id: int) -> bool:
        """
        Check if student can enroll in a course.

        Args:
            course_id: ID of the course

        Returns:
            bool: True if student can enroll

        Note:
            This should check prerequisites, capacity, etc.
        """
        return True

    def __repr__(self) -> str:
        """String representation of Student."""
        return f"<Student(user_id={self.user_id}, grade_level='{self.grade_level}')>"


class Parent(BaseModel):
    """
    Parent user class demonstrating inheritance and polymorphism.

    Parents can view their children's academic information and manage payments.
    """

    __tablename__ = "parents"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    phone_number = Column(String(20))
    address = Column(String(255))

    # Relationship to User
    user = relationship("User", backref="parent_profile", foreign_keys=[user_id])

    @property
    def username(self) -> str:
        """Get username from associated User."""
        return self.user.username if self.user else ""

    @property
    def full_name(self) -> str:
        """Get full name from associated User."""
        return self.user.full_name if self.user else ""

    # Encapsulation: Private phone number with getter/setter
    @property
    def contact_number(self) -> str:
        """
        Get parent's phone number.

        Returns:
            str: Phone number
        """
        return self.phone_number if self.phone_number else ""

    @contact_number.setter
    def contact_number(self, value: str):
        """
        Set parent's phone number.

        Args:
            value: New phone number
        """
        self.phone_number = value

    def get_permissions(self) -> list[str]:
        """
        Override: Parents can view children's data and manage payments.

        Returns:
            list[str]: List of parent-specific permissions
        """
        return [
            "view_profile", "edit_profile",
            "view_children", "view_children_grades",
            "view_children_tasks", "manage_payments",
            "view_reports"
        ]

    def can_view_child_data(self, student_id: int) -> bool:
        """
        Check if parent can view a specific child's data.

        Args:
            student_id: ID of the student

        Returns:
            bool: True if this is their child

        Note:
            This should check the parent-child relationship
        """
        return any(child.user_id == student_id for child in self.children)

    def __repr__(self) -> str:
        """String representation of Parent."""
        return f"<Parent(user_id={self.user_id}, phone='{self.phone_number}')>"


class Worker(BaseModel):
    """
    Worker user class demonstrating inheritance and polymorphism.

    Workers handle administrative and maintenance tasks.
    """

    __tablename__ = "workers"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    job_title = Column(String(100))
    hire_date = Column(Date)
    hourly_rate = Column(DECIMAL(10, 2))

    # Relationship to User
    user = relationship("User", backref="worker_profile", foreign_keys=[user_id])

    @property
    def username(self) -> str:
        """Get username from associated User."""
        return self.user.username if self.user else ""

    @property
    def full_name(self) -> str:
        """Get full name from associated User."""
        return self.user.full_name if self.user else ""

    # Encapsulation: Private hourly rate with getter/setter
    @property
    def rate(self) -> Decimal:
        """
        Get worker's hourly rate.

        Returns:
            Decimal: Hourly rate
        """
        return self.hourly_rate if self.hourly_rate else Decimal("0.00")

    @rate.setter
    def rate(self, value: Decimal):
        """
        Set worker's hourly rate.

        Args:
            value: New hourly rate
        """
        self.hourly_rate = value

    def get_permissions(self) -> list[str]:
        """
        Override: Workers have task and schedule permissions.

        Returns:
            list[str]: List of worker-specific permissions
        """
        return [
            "view_profile", "edit_profile",
            "view_my_tasks", "view_my_schedule",
            "view_my_payments"
        ]

    def calculate_pay(self, hours_worked: float) -> Decimal:
        """
        Calculate pay for hours worked.

        Args:
            hours_worked: Number of hours worked

        Returns:
            Decimal: Total pay amount
        """
        return self.rate * Decimal(str(hours_worked))

    def __repr__(self) -> str:
        """String representation of Worker."""
        return f"<Worker(user_id={self.user_id}, job_title='{self.job_title}')>"
