"""
Enrollment and queue management service.

This module handles course enrollment, waiting lists (queues), and automatic
queue progression when slots become available.
"""

from typing import List, Optional, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.course import Course, CourseEnrollment, EnrollmentStatus
from app.models.user import Student
from app.models.queue import Queue, QueueItem, QueueType, QueueItemStatus


class EnrollmentService:
    """
    Service class for enrollment and queue management.

    Provides methods for:
    - Student enrollment in courses
    - Automatic queue management when courses are full
    - Auto-promotion from queue when slots open
    """

    @staticmethod
    def enroll_student(
        student_id: int,
        course_id: int,
        db: Session
    ) -> Tuple[bool, Optional[str], Optional[dict]]:
        """
        Enroll a student in a course or add to waiting list if full.

        Args:
            student_id: Student user ID
            course_id: Course ID
            db: Database session

        Returns:
            tuple: (success bool, message or error, enrollment/queue info dict)
                  enrollment/queue info contains:
                  - 'enrolled': bool - True if enrolled, False if queued
                  - 'position': int - Queue position if queued
        """
        try:
            # Validate student exists
            student = db.query(Student).filter(Student.user_id == student_id).first()
            if not student:
                return False, "Student not found.", None

            # Validate course exists
            course = db.query(Course).filter(Course.id == course_id).first()
            if not course:
                return False, "Course not found.", None

            # Check if already enrolled
            existing_enrollment = db.query(CourseEnrollment).filter(
                CourseEnrollment.student_id == student_id,
                CourseEnrollment.course_id == course_id,
                CourseEnrollment.status == EnrollmentStatus.ACTIVE
            ).first()

            if existing_enrollment:
                return False, "Student is already enrolled in this course.", None

            # Check if already in queue for this course
            course_queue = EnrollmentService._get_or_create_course_queue(course_id, db)
            existing_queue_item = db.query(QueueItem).filter(
                QueueItem.queue_id == course_queue.id,
                QueueItem.user_id == student_id,
                QueueItem.status == QueueItemStatus.WAITING
            ).first()

            if existing_queue_item:
                return False, f"Student is already in the waiting list at position {existing_queue_item.position}.", None

            # Check if course has available slots
            if course.can_enroll_student():
                # Enroll directly
                enrollment = CourseEnrollment(
                    student_id=student_id,
                    course_id=course_id,
                    enrollment_date=datetime.utcnow(),
                    status=EnrollmentStatus.ACTIVE
                )
                db.add(enrollment)
                db.commit()
                db.refresh(enrollment)

                return True, "Student enrolled successfully.", {'enrolled': True, 'position': None}
            else:
                # Add to waiting list
                queue_item = EnrollmentService._add_to_course_queue(
                    student_id, course_id, course_queue, db
                )
                return True, f"Course is full. Student added to waiting list at position {queue_item.position}.", {
                    'enrolled': False,
                    'position': queue_item.position
                }

        except Exception as e:
            db.rollback()
            return False, f"Error enrolling student: {str(e)}", None

    @staticmethod
    def drop_enrollment(
        enrollment_id: int,
        db: Session
    ) -> Tuple[bool, Optional[str]]:
        """
        Drop a student's enrollment and auto-promote from queue if available.

        Args:
            enrollment_id: Enrollment ID
            db: Database session

        Returns:
            tuple: (success bool, message or error)
        """
        try:
            enrollment = db.query(CourseEnrollment).filter(
                CourseEnrollment.id == enrollment_id
            ).first()

            if not enrollment:
                return False, "Enrollment not found."

            if enrollment.status != EnrollmentStatus.ACTIVE:
                return False, "Enrollment is not active."

            course_id = enrollment.course_id

            # Mark enrollment as dropped
            enrollment.mark_dropped()
            db.commit()

            # Try to auto-promote from queue
            EnrollmentService._promote_from_queue(course_id, db)

            return True, "Enrollment dropped successfully. Next student in queue has been notified."

        except Exception as e:
            db.rollback()
            return False, f"Error dropping enrollment: {str(e)}"

    @staticmethod
    def _get_or_create_course_queue(course_id: int, db: Session) -> Queue:
        """
        Get or create a queue for a course.

        Args:
            course_id: Course ID
            db: Database session

        Returns:
            Queue: Course queue object
        """
        # Check if queue exists
        queue_name = f"Course_{course_id}_Queue"
        queue = db.query(Queue).filter(Queue.queue_name == queue_name).first()

        if not queue:
            # Create new queue
            queue = Queue(
                queue_name=queue_name,
                description=f"Waiting list for course ID {course_id}",
                queue_type=QueueType.REGISTRATION,
                max_capacity=0  # Unlimited
            )
            db.add(queue)
            db.commit()
            db.refresh(queue)

        return queue

    @staticmethod
    def _add_to_course_queue(
        student_id: int,
        course_id: int,
        course_queue: Queue,
        db: Session
    ) -> QueueItem:
        """
        Add a student to the course waiting list.

        Args:
            student_id: Student user ID
            course_id: Course ID
            course_queue: Course queue object
            db: Database session

        Returns:
            QueueItem: Created queue item
        """
        position = course_queue.next_position

        queue_item = QueueItem(
            queue_id=course_queue.id,
            user_id=student_id,
            position=position,
            status=QueueItemStatus.WAITING,
            priority=0,
            joined_at=datetime.utcnow(),
            notes=f"Waiting for course ID {course_id}"
        )

        db.add(queue_item)
        db.commit()
        db.refresh(queue_item)

        return queue_item

    @staticmethod
    def _promote_from_queue(course_id: int, db: Session) -> bool:
        """
        Automatically promote the next student from queue to enrollment.

        Args:
            course_id: Course ID
            db: Database session

        Returns:
            bool: True if a student was promoted, False otherwise
        """
        try:
            # Get course
            course = db.query(Course).filter(Course.id == course_id).first()
            if not course or not course.can_enroll_student():
                return False

            # Get course queue
            queue_name = f"Course_{course_id}_Queue"
            course_queue = db.query(Queue).filter(Queue.queue_name == queue_name).first()
            if not course_queue:
                return False

            # Get next waiting student
            next_item = course_queue.get_next_waiting_item()
            if not next_item:
                return False

            # Enroll the student
            enrollment = CourseEnrollment(
                student_id=next_item.user_id,
                course_id=course_id,
                enrollment_date=datetime.utcnow(),
                status=EnrollmentStatus.ACTIVE
            )
            db.add(enrollment)

            # Mark queue item as completed
            next_item.mark_completed()

            db.commit()

            return True

        except Exception as e:
            db.rollback()
            print(f"Error promoting from queue: {str(e)}")
            return False

    @staticmethod
    def get_student_queue_position(student_id: int, course_id: int, db: Session) -> Optional[int]:
        """
        Get a student's position in a course waiting list.

        Args:
            student_id: Student user ID
            course_id: Course ID
            db: Database session

        Returns:
            Optional[int]: Queue position or None if not in queue
        """
        try:
            queue_name = f"Course_{course_id}_Queue"
            course_queue = db.query(Queue).filter(Queue.queue_name == queue_name).first()
            if not course_queue:
                return None

            queue_item = db.query(QueueItem).filter(
                QueueItem.queue_id == course_queue.id,
                QueueItem.user_id == student_id,
                QueueItem.status == QueueItemStatus.WAITING
            ).first()

            return queue_item.position if queue_item else None

        except Exception as e:
            print(f"Error getting queue position: {str(e)}")
            return None

    @staticmethod
    def get_course_queue_info(course_id: int, db: Session) -> dict:
        """
        Get information about a course's waiting list.

        Args:
            course_id: Course ID
            db: Database session

        Returns:
            dict: Queue information including count and list of waiting students
        """
        try:
            queue_name = f"Course_{course_id}_Queue"
            course_queue = db.query(Queue).filter(Queue.queue_name == queue_name).first()

            if not course_queue:
                return {
                    'waiting_count': 0,
                    'waiting_students': [],
                    'needs_new_class': False
                }

            # Get waiting students
            waiting_items = db.query(QueueItem).filter(
                QueueItem.queue_id == course_queue.id,
                QueueItem.status == QueueItemStatus.WAITING
            ).order_by(QueueItem.position).all()

            waiting_students = [
                {
                    'student_id': item.user_id,
                    'student_name': item.user_name,
                    'position': item.position,
                    'joined_at': item.joined_at,
                    'wait_time_minutes': item.wait_time_minutes
                }
                for item in waiting_items
            ]

            waiting_count = len(waiting_students)

            return {
                'waiting_count': waiting_count,
                'waiting_students': waiting_students,
                'needs_new_class': waiting_count >= 5  # Suggest new class when 5+ waiting
            }

        except Exception as e:
            print(f"Error getting course queue info: {str(e)}")
            return {
                'waiting_count': 0,
                'waiting_students': [],
                'needs_new_class': False
            }

    @staticmethod
    def get_all_course_queues_summary(db: Session) -> List[dict]:
        """
        Get summary of all course queues for manager view.

        Args:
            db: Database session

        Returns:
            List[dict]: List of queue summaries with course info
        """
        try:
            # Get all courses
            courses = db.query(Course).all()
            summaries = []

            for course in courses:
                queue_info = EnrollmentService.get_course_queue_info(course.id, db)
                summaries.append({
                    'course_id': course.id,
                    'course_name': course.course_name,
                    'course_code': course.course_code,
                    'capacity': course.capacity,
                    'enrolled_count': course.enrolled_count,
                    'available_slots': course.available_slots,
                    'waiting_count': queue_info['waiting_count'],
                    'needs_new_class': queue_info['needs_new_class']
                })

            return summaries

        except Exception as e:
            print(f"Error getting queue summaries: {str(e)}")
            return []

    @staticmethod
    def get_student_courses_and_queues(student_id: int, db: Session) -> dict:
        """
        Get all courses a student is enrolled in or queued for.

        Args:
            student_id: Student user ID
            db: Database session

        Returns:
            dict: Contains 'enrolled_courses' and 'queued_courses' lists
        """
        try:
            # Get enrolled courses
            enrollments = db.query(CourseEnrollment).filter(
                CourseEnrollment.student_id == student_id,
                CourseEnrollment.status == EnrollmentStatus.ACTIVE
            ).all()

            enrolled_courses = [
                {
                    'enrollment_id': e.id,
                    'course_id': e.course_id,
                    'course_name': e.course.course_name,
                    'course_code': e.course.course_code,
                    'teacher_name': e.course.teacher_name,
                    'enrollment_date': e.enrollment_date
                }
                for e in enrollments
            ]

            # Get queued courses
            queue_items = db.query(QueueItem).filter(
                QueueItem.user_id == student_id,
                QueueItem.status == QueueItemStatus.WAITING
            ).all()

            queued_courses = []
            for item in queue_items:
                # Extract course_id from queue name (format: Course_{course_id}_Queue)
                if item.queue and item.queue.queue_name.startswith("Course_"):
                    try:
                        course_id = int(item.queue.queue_name.split("_")[1])
                        course = db.query(Course).filter(Course.id == course_id).first()
                        if course:
                            queued_courses.append({
                                'queue_item_id': item.id,
                                'course_id': course.id,
                                'course_name': course.course_name,
                                'course_code': course.course_code,
                                'position': item.position,
                                'joined_at': item.joined_at,
                                'wait_time_minutes': item.wait_time_minutes
                            })
                    except (IndexError, ValueError):
                        continue

            return {
                'enrolled_courses': enrolled_courses,
                'queued_courses': queued_courses
            }

        except Exception as e:
            print(f"Error getting student courses and queues: {str(e)}")
            return {
                'enrolled_courses': [],
                'queued_courses': []
            }
