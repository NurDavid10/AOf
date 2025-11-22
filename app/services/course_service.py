"""
Course management service.

This module handles course CRUD operations, enrollment management,
and course-related business logic.
"""

from typing import List, Optional, Tuple
from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.course import Course, CourseEnrollment, EnrollmentStatus
from app.models.user import Teacher, Student


class CourseService:
    """
    Service class for course management operations.

    Provides methods for:
    - Course CRUD operations
    - Enrollment management
    - Course capacity checking
    """

    @staticmethod
    def create_course(
        course_name: str,
        course_code: str,
        description: Optional[str],
        teacher_id: Optional[int],
        capacity: int,
        fee: Decimal,
        start_date: Optional[datetime],
        end_date: Optional[datetime],
        db: Session
    ) -> Tuple[Optional[Course], Optional[str]]:
        """
        Create a new course.

        Args:
            course_name: Name of the course
            course_code: Unique course code
            description: Course description
            teacher_id: ID of the assigned teacher (Teacher.user_id)
            capacity: Maximum number of students
            fee: Course fee
            start_date: Course start date
            end_date: Course end date
            db: Database session

        Returns:
            tuple: (Course object or None, error message or None)
        """
        try:
            # Validate course code uniqueness
            existing = db.query(Course).filter(Course.course_code == course_code).first()
            if existing:
                return None, "Course code already exists. Please choose a different code."

            # Validate teacher exists if provided
            if teacher_id:
                teacher = db.query(Teacher).filter(Teacher.user_id == teacher_id).first()
                if not teacher:
                    return None, "Teacher not found."

            # Create course
            course = Course(
                course_name=course_name,
                course_code=course_code,
                description=description,
                teacher_id=teacher_id,
                capacity=capacity,
                fee=fee,
                start_date=start_date,
                end_date=end_date
            )

            db.add(course)
            db.commit()
            db.refresh(course)

            return course, None

        except IntegrityError as e:
            db.rollback()
            return None, "Database constraint violation. Course code may already exist."
        except Exception as e:
            db.rollback()
            return None, f"Error creating course: {str(e)}"

    @staticmethod
    def get_all_courses(db: Session) -> List[Course]:
        """
        Get all courses.

        Args:
            db: Database session

        Returns:
            List[Course]: List of all courses
        """
        try:
            return db.query(Course).all()
        except Exception as e:
            print(f"Error getting all courses: {str(e)}")
            return []

    @staticmethod
    def get_course_by_id(course_id: int, db: Session) -> Optional[Course]:
        """
        Get course by ID.

        Args:
            course_id: Course ID
            db: Database session

        Returns:
            Optional[Course]: Course object if found, None otherwise
        """
        try:
            return db.query(Course).filter(Course.id == course_id).first()
        except Exception as e:
            print(f"Error getting course by ID: {str(e)}")
            return None

    @staticmethod
    def get_course_by_code(course_code: str, db: Session) -> Optional[Course]:
        """
        Get course by code.

        Args:
            course_code: Course code
            db: Database session

        Returns:
            Optional[Course]: Course object if found, None otherwise
        """
        try:
            return db.query(Course).filter(Course.course_code == course_code).first()
        except Exception as e:
            print(f"Error getting course by code: {str(e)}")
            return None

    @staticmethod
    def update_course(
        course_id: int,
        course_name: Optional[str] = None,
        description: Optional[str] = None,
        teacher_id: Optional[int] = None,
        capacity: Optional[int] = None,
        fee: Optional[Decimal] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        db: Session = None
    ) -> Tuple[Optional[Course], Optional[str]]:
        """
        Update course information.

        Args:
            course_id: Course ID
            course_name: New course name (optional)
            description: New description (optional)
            teacher_id: New teacher ID (optional)
            capacity: New capacity (optional)
            fee: New fee (optional)
            start_date: New start date (optional)
            end_date: New end date (optional)
            db: Database session

        Returns:
            tuple: (Updated Course object or None, error message or None)
        """
        try:
            course = db.query(Course).filter(Course.id == course_id).first()

            if not course:
                return None, "Course not found"

            # Validate teacher if provided
            if teacher_id is not None:
                teacher = db.query(Teacher).filter(Teacher.user_id == teacher_id).first()
                if not teacher:
                    return None, "Teacher not found."

            # Update fields
            if course_name is not None:
                course.course_name = course_name
            if description is not None:
                course.description = description
            if teacher_id is not None:
                course.teacher_id = teacher_id
            if capacity is not None:
                course.capacity = capacity
            if fee is not None:
                course.fee = fee
            if start_date is not None:
                course.start_date = start_date
            if end_date is not None:
                course.end_date = end_date

            db.commit()
            db.refresh(course)

            return course, None

        except Exception as e:
            db.rollback()
            return None, f"Error updating course: {str(e)}"

    @staticmethod
    def delete_course(course_id: int, db: Session) -> Tuple[bool, Optional[str]]:
        """
        Delete a course.

        Args:
            course_id: Course ID
            db: Database session

        Returns:
            tuple: (Success boolean, error message or None)
        """
        try:
            course = db.query(Course).filter(Course.id == course_id).first()

            if not course:
                return False, "Course not found"

            db.delete(course)
            db.commit()

            return True, None

        except Exception as e:
            db.rollback()
            return False, f"Error deleting course: {str(e)}"

    @staticmethod
    def get_courses_by_teacher(teacher_id: int, db: Session) -> List[Course]:
        """
        Get all courses taught by a specific teacher.

        Args:
            teacher_id: Teacher user ID
            db: Database session

        Returns:
            List[Course]: List of courses
        """
        try:
            return db.query(Course).filter(Course.teacher_id == teacher_id).all()
        except Exception as e:
            print(f"Error getting courses by teacher: {str(e)}")
            return []

    @staticmethod
    def get_student_enrollments(student_id: int, db: Session) -> List[CourseEnrollment]:
        """
        Get all enrollments for a student.

        Args:
            student_id: Student user ID
            db: Database session

        Returns:
            List[CourseEnrollment]: List of enrollments
        """
        try:
            return db.query(CourseEnrollment).filter(
                CourseEnrollment.student_id == student_id
            ).all()
        except Exception as e:
            print(f"Error getting student enrollments: {str(e)}")
            return []

    @staticmethod
    def get_course_enrollments(course_id: int, db: Session) -> List[CourseEnrollment]:
        """
        Get all enrollments for a course.

        Args:
            course_id: Course ID
            db: Database session

        Returns:
            List[CourseEnrollment]: List of enrollments
        """
        try:
            return db.query(CourseEnrollment).filter(
                CourseEnrollment.course_id == course_id
            ).all()
        except Exception as e:
            print(f"Error getting course enrollments: {str(e)}")
            return []

    @staticmethod
    def is_student_enrolled(student_id: int, course_id: int, db: Session) -> bool:
        """
        Check if a student is enrolled in a course.

        Args:
            student_id: Student user ID
            course_id: Course ID
            db: Database session

        Returns:
            bool: True if enrolled, False otherwise
        """
        try:
            enrollment = db.query(CourseEnrollment).filter(
                CourseEnrollment.student_id == student_id,
                CourseEnrollment.course_id == course_id,
                CourseEnrollment.status == EnrollmentStatus.ACTIVE
            ).first()
            return enrollment is not None
        except Exception as e:
            print(f"Error checking enrollment: {str(e)}")
            return False
