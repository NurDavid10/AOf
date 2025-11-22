"""
Course and enrollment models.

This module handles course management, enrollments, and related functionality.
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey, Date, DECIMAL, Enum, DateTime
from sqlalchemy.orm import relationship
import enum
from decimal import Decimal
from app.models.base import BaseModel


class EnrollmentStatus(str, enum.Enum):
    """Enumeration of enrollment statuses."""
    ACTIVE = "active"
    COMPLETED = "completed"
    DROPPED = "dropped"


class Course(BaseModel):
    """
    Course model representing educational courses.

    Attributes:
        course_name: Name of the course
        course_code: Unique course code
        description: Detailed course description
        teacher_id: ID of the assigned teacher
        capacity: Maximum number of students
        start_date: Course start date
        end_date: Course end date
        fee: Course fee amount
    """

    __tablename__ = "courses"

    course_name = Column(String(100), nullable=False)
    course_code = Column(String(20), unique=True, index=True)
    description = Column(Text)
    teacher_id = Column(Integer, ForeignKey("teachers.user_id", ondelete="SET NULL"), nullable=True)
    capacity = Column(Integer, default=30)
    start_date = Column(Date)
    end_date = Column(Date)
    fee = Column(DECIMAL(10, 2))

    # Relationships
    teacher = relationship("Teacher", backref="courses", foreign_keys=[teacher_id])
    enrollments = relationship("CourseEnrollment", back_populates="course", cascade="all, delete-orphan")

    @property
    def teacher_name(self) -> str:
        """
        Get the name of the assigned teacher.

        Returns:
            str: Teacher's full name or "Unassigned" if no teacher
        """
        if self.teacher and self.teacher.user:
            return self.teacher.user.full_name
        return "Unassigned"

    @property
    def enrolled_count(self) -> int:
        """
        Get the number of currently enrolled students.

        Returns:
            int: Number of active enrollments
        """
        return sum(1 for e in self.enrollments if e.status == EnrollmentStatus.ACTIVE)

    @property
    def is_full(self) -> bool:
        """
        Check if the course is at full capacity.

        Returns:
            bool: True if course is full, False otherwise
        """
        return self.enrolled_count >= self.capacity

    @property
    def available_slots(self) -> int:
        """
        Get the number of available slots in the course.

        Returns:
            int: Number of available slots
        """
        return max(0, self.capacity - self.enrolled_count)

    @property
    def fee_amount(self) -> Decimal:
        """
        Get the course fee.

        Returns:
            Decimal: Course fee amount
        """
        return self.fee if self.fee else Decimal("0.00")

    def can_enroll_student(self) -> bool:
        """
        Check if a new student can enroll in this course.

        Returns:
            bool: True if enrollment is possible, False otherwise
        """
        return not self.is_full

    def __repr__(self) -> str:
        """String representation of Course."""
        return f"<Course(id={self.id}, code='{self.course_code}', name='{self.course_name}')>"


class CourseEnrollment(BaseModel):
    """
    Course enrollment model linking students to courses.

    Attributes:
        student_id: ID of the enrolled student
        course_id: ID of the course
        enrollment_date: Date of enrollment
        status: Current enrollment status
    """

    __tablename__ = "course_enrollments"

    student_id = Column(Integer, ForeignKey("students.user_id", ondelete="CASCADE"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    enrollment_date = Column(DateTime)
    status = Column(Enum(EnrollmentStatus), default=EnrollmentStatus.ACTIVE, nullable=False)

    # Relationships
    student = relationship("Student", backref="enrollments", foreign_keys=[student_id])
    course = relationship("Course", back_populates="enrollments", foreign_keys=[course_id])

    @property
    def student_name(self) -> str:
        """
        Get the enrolled student's name.

        Returns:
            str: Student's full name
        """
        if self.student and self.student.user:
            return self.student.user.full_name
        return "Unknown"

    @property
    def course_name(self) -> str:
        """
        Get the course name.

        Returns:
            str: Course name
        """
        return self.course.course_name if self.course else "Unknown"

    @property
    def is_active(self) -> bool:
        """
        Check if enrollment is currently active.

        Returns:
            bool: True if enrollment is active, False otherwise
        """
        return self.status == EnrollmentStatus.ACTIVE

    def mark_completed(self):
        """Mark this enrollment as completed."""
        self.status = EnrollmentStatus.COMPLETED

    def mark_dropped(self):
        """Mark this enrollment as dropped."""
        self.status = EnrollmentStatus.DROPPED

    def __repr__(self) -> str:
        """String representation of CourseEnrollment."""
        return f"<CourseEnrollment(id={self.id}, student_id={self.student_id}, course_id={self.course_id})>"
