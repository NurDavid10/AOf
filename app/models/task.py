"""
Task and submission models.

This module handles tasks, assignments, exams, and student submissions.
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, DECIMAL, Enum
from sqlalchemy.orm import relationship
import enum
from decimal import Decimal
from datetime import datetime
from app.models.base import BaseModel


class TaskType(str, enum.Enum):
    """Enumeration of task types."""
    ASSIGNMENT = "assignment"
    EXAM = "exam"
    PROJECT = "project"
    HOMEWORK = "homework"


class Task(BaseModel):
    """
    Task model representing assignments, exams, projects, etc.

    Attributes:
        title: Task title
        description: Detailed task description
        course_id: ID of the associated course
        due_date: Task due date and time
        created_by: ID of the user who created the task
        task_type: Type of task (assignment, exam, etc.)
        max_points: Maximum points for this task
    """

    __tablename__ = "tasks"

    title = Column(String(200), nullable=False)
    description = Column(Text)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    due_date = Column(DateTime)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    task_type = Column(Enum(TaskType), default=TaskType.ASSIGNMENT, nullable=False)
    max_points = Column(DECIMAL(5, 2), default=100.00)

    # Relationships
    course = relationship("Course", backref="tasks", foreign_keys=[course_id])
    creator = relationship("User", backref="created_tasks", foreign_keys=[created_by])
    submissions = relationship("TaskSubmission", back_populates="task", cascade="all, delete-orphan")

    @property
    def course_name(self) -> str:
        """
        Get the associated course name.

        Returns:
            str: Course name
        """
        return self.course.course_name if self.course else "Unknown"

    @property
    def creator_name(self) -> str:
        """
        Get the name of the task creator.

        Returns:
            str: Creator's full name
        """
        return self.creator.full_name if self.creator else "Unknown"

    @property
    def is_overdue(self) -> bool:
        """
        Check if the task is past its due date.

        Returns:
            bool: True if task is overdue, False otherwise
        """
        if not self.due_date:
            return False
        return datetime.utcnow() > self.due_date

    @property
    def submission_count(self) -> int:
        """
        Get the number of submissions for this task.

        Returns:
            int: Number of submissions
        """
        return len(self.submissions) if self.submissions else 0

    @property
    def graded_count(self) -> int:
        """
        Get the number of graded submissions.

        Returns:
            int: Number of graded submissions
        """
        return sum(1 for s in self.submissions if s.is_graded)

    def get_submission_for_student(self, student_id: int):
        """
        Get a student's submission for this task.

        Args:
            student_id: ID of the student

        Returns:
            TaskSubmission or None: The submission if it exists
        """
        for submission in self.submissions:
            if submission.student_id == student_id:
                return submission
        return None

    def __repr__(self) -> str:
        """String representation of Task."""
        return f"<Task(id={self.id}, title='{self.title}', type='{self.task_type.value}')>"


class TaskSubmission(BaseModel):
    """
    Task submission model representing student submissions.

    Attributes:
        task_id: ID of the associated task
        student_id: ID of the student who submitted
        submission_date: Date and time of submission
        submission_text: Text content of the submission
        grade: Grade received (nullable until graded)
        feedback: Teacher's feedback on the submission
    """

    __tablename__ = "task_submissions"

    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.user_id", ondelete="CASCADE"), nullable=False)
    submission_date = Column(DateTime, default=datetime.utcnow)
    submission_text = Column(Text)
    grade = Column(DECIMAL(5, 2), nullable=True)
    feedback = Column(Text)

    # Relationships
    task = relationship("Task", back_populates="submissions", foreign_keys=[task_id])
    student = relationship("Student", backref="submissions", foreign_keys=[student_id])

    @property
    def student_name(self) -> str:
        """
        Get the student's name.

        Returns:
            str: Student's full name
        """
        if self.student and self.student.user:
            return self.student.user.full_name
        return "Unknown"

    @property
    def task_title(self) -> str:
        """
        Get the task title.

        Returns:
            str: Task title
        """
        return self.task.title if self.task else "Unknown"

    @property
    def is_graded(self) -> bool:
        """
        Check if the submission has been graded.

        Returns:
            bool: True if graded, False otherwise
        """
        return self.grade is not None

    @property
    def grade_percentage(self) -> float:
        """
        Calculate grade as a percentage.

        Returns:
            float: Grade percentage (0-100)
        """
        if self.grade is None or not self.task or not self.task.max_points:
            return 0.0
        return float((self.grade / self.task.max_points) * 100)

    @property
    def was_late(self) -> bool:
        """
        Check if submission was submitted after the due date.

        Returns:
            bool: True if submitted late, False otherwise
        """
        if not self.task or not self.task.due_date or not self.submission_date:
            return False
        return self.submission_date > self.task.due_date

    def assign_grade(self, grade: Decimal, feedback: str = ""):
        """
        Assign a grade to this submission.

        Args:
            grade: Grade value
            feedback: Optional feedback text
        """
        self.grade = grade
        if feedback:
            self.feedback = feedback

    def __repr__(self) -> str:
        """String representation of TaskSubmission."""
        return f"<TaskSubmission(id={self.id}, task_id={self.task_id}, student_id={self.student_id})>"
