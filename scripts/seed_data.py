"""
Database seeding script with dummy data.

This script populates the database with sample data for testing.
"""

import sys
from pathlib import Path
from datetime import datetime, date, timedelta
from decimal import Decimal

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import get_db_context
from app.models.user import User, Manager, Teacher, Student, Parent, Worker, UserRole
from app.models.course import Course, CourseEnrollment, EnrollmentStatus
from app.models.task import Task, TaskSubmission, TaskType
from app.models.payment import Payment, PaymentType, PaymentMethod, PaymentStatus
from app.models.queue import Queue, QueueItem, QueueType, QueueItemStatus
from app.models.expense import Expense, ExpenseCategory
from app.models.maintenance_task import MaintenanceTask, TaskPriority, TaskStatus
from app.services.auth_service import AuthService


def seed_users(db):
    """Create sample users with all roles."""
    print("\n[1/6] Creating users...")

    users_data = [
        # Managers
        ("manager1", "password123", "manager1@academic.com", "Alice Manager", UserRole.MANAGER),
        ("director1", "password123", "director1@academic.com", "Bob Director", UserRole.MANAGER),
        # Teachers
        ("teacher1", "password123", "teacher1@academic.com", "Carol Math", UserRole.TEACHER),
        ("teacher2", "password123", "teacher2@academic.com", "David Science", UserRole.TEACHER),
        ("teacher3", "password123", "teacher3@academic.com", "Emma English", UserRole.TEACHER),
        ("teacher4", "password123", "teacher4@academic.com", "Frank History", UserRole.TEACHER),
        ("teacher5", "password123", "teacher5@academic.com", "Grace Art", UserRole.TEACHER),
        # Students
        ("student1", "password123", "student1@academic.com", "Harry Potter", UserRole.STUDENT),
        ("student2", "password123", "student2@academic.com", "Hermione Granger", UserRole.STUDENT),
        ("student3", "password123", "student3@academic.com", "Ron Weasley", UserRole.STUDENT),
        ("student4", "password123", "student4@academic.com", "Luna Lovegood", UserRole.STUDENT),
        ("student5", "password123", "student5@academic.com", "Neville Longbottom", UserRole.STUDENT),
        ("student6", "password123", "student6@academic.com", "Ginny Weasley", UserRole.STUDENT),
        ("student7", "password123", "student7@academic.com", "Draco Malfoy", UserRole.STUDENT),
        ("student8", "password123", "student8@academic.com", "Cho Chang", UserRole.STUDENT),
        ("student9", "password123", "student9@academic.com", "Dean Thomas", UserRole.STUDENT),
        ("student10", "password123", "student10@academic.com", "Seamus Finnigan", UserRole.STUDENT),
        # Parents
        ("parent1", "password123", "parent1@academic.com", "James Potter Sr", UserRole.PARENT),
        ("parent2", "password123", "parent2@academic.com", "Arthur Weasley", UserRole.PARENT),
        ("parent3", "password123", "parent3@academic.com", "Xenophilius Lovegood", UserRole.PARENT),
        # Workers
        ("worker1", "password123", "worker1@academic.com", "Argus Filch", UserRole.WORKER),
        ("worker2", "password123", "worker2@academic.com", "Rubeus Hagrid", UserRole.WORKER),
        ("worker3", "password123", "worker3@academic.com", "Poppy Pomfrey", UserRole.WORKER),
    ]

    users = []
    for username, password, email, full_name, role in users_data:
        password_hash = AuthService.hash_password(password)
        user = User(
            username=username,
            password_hash=password_hash,
            email=email,
            full_name=full_name,
            role=role
        )
        db.add(user)
        users.append((user, role))

    db.commit()
    print(f"✓ Created {len(users)} users")
    return users


def seed_role_profiles(db, users):
    """Create role-specific profiles."""
    print("\n[2/6] Creating role profiles...")

    count = 0

    for user_obj, role in users:
        db.refresh(user_obj)  # Refresh to get the ID

        if role == UserRole.MANAGER:
            manager = Manager(
                user_id=user_obj.id,
                department="Administration" if "manager" in user_obj.username else "Operations",
                access_level=10 if "director" in user_obj.username else 5
            )
            db.add(manager)
            count += 1

        elif role == UserRole.TEACHER:
            subject = "Mathematics" if "Math" in user_obj.full_name else \
                     "Science" if "Science" in user_obj.full_name else \
                     "English" if "English" in user_obj.full_name else \
                     "History" if "History" in user_obj.full_name else "Art"

            teacher = Teacher(
                user_id=user_obj.id,
                subject_specialization=subject,
                hire_date=date.today() - timedelta(days=365),
                salary=Decimal("5000.00")
            )
            db.add(teacher)
            count += 1

        elif role == UserRole.STUDENT:
            student = Student(
                user_id=user_obj.id,
                enrollment_date=date.today() - timedelta(days=30),
                grade_level="Grade 10",
                parent_id=None  # Will update later
            )
            db.add(student)
            count += 1

        elif role == UserRole.PARENT:
            parent = Parent(
                user_id=user_obj.id,
                phone_number=f"+1-555-{1000 + user_obj.id:04d}",
                address=f"{user_obj.id * 100} Main Street, City, State"
            )
            db.add(parent)
            count += 1

        elif role == UserRole.WORKER:
            worker = Worker(
                user_id=user_obj.id,
                job_title="Maintenance" if "Filch" in user_obj.full_name else \
                         "Groundskeeper" if "Hagrid" in user_obj.full_name else "Nurse",
                hire_date=date.today() - timedelta(days=730),
                hourly_rate=Decimal("25.00")
            )
            db.add(worker)
            count += 1

    db.commit()
    print(f"✓ Created {count} role profiles")


def seed_courses(db):
    """Create sample courses."""
    print("\n[3/6] Creating courses...")

    # Get teachers
    teachers = db.query(Teacher).all()

    courses_data = [
        ("Introduction to Algebra", "MATH101", "Basic algebra concepts", teachers[0].user_id if len(teachers) > 0 else None, 30, Decimal("500.00")),
        ("Physics Fundamentals", "SCI101", "Introduction to physics", teachers[1].user_id if len(teachers) > 1 else None, 25, Decimal("550.00")),
        ("English Literature", "ENG101", "Classic literature study", teachers[2].user_id if len(teachers) > 2 else None, 30, Decimal("450.00")),
        ("World History", "HIST101", "World history overview", teachers[3].user_id if len(teachers) > 3 else None, 28, Decimal("450.00")),
        ("Digital Art", "ART101", "Introduction to digital art", teachers[4].user_id if len(teachers) > 4 else None, 20, Decimal("600.00")),
        ("Advanced Mathematics", "MATH201", "Advanced math topics", teachers[0].user_id if len(teachers) > 0 else None, 20, Decimal("650.00")),
        ("Chemistry Basics", "SCI201", "Introduction to chemistry", teachers[1].user_id if len(teachers) > 1 else None, 25, Decimal("600.00")),
        ("Creative Writing", "ENG201", "Creative writing workshop", teachers[2].user_id if len(teachers) > 2 else None, 15, Decimal("500.00")),
    ]

    courses = []
    for name, code, desc, teacher_id, capacity, fee in courses_data:
        course = Course(
            course_name=name,
            course_code=code,
            description=desc,
            teacher_id=teacher_id,
            capacity=capacity,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=90),
            fee=fee
        )
        db.add(course)
        courses.append(course)

    db.commit()
    print(f"✓ Created {len(courses)} courses")
    return courses


def seed_enrollments(db, courses):
    """Create course enrollments."""
    print("\n[4/6] Creating enrollments...")

    students = db.query(Student).all()
    count = 0

    for student in students[:8]:  # Enroll first 8 students
        # Enroll each student in 2-3 courses
        for course in courses[:3]:
            enrollment = CourseEnrollment(
                student_id=student.user_id,
                course_id=course.id,
                enrollment_date=datetime.utcnow(),
                status=EnrollmentStatus.ACTIVE
            )
            db.add(enrollment)
            count += 1

    db.commit()
    print(f"✓ Created {count} enrollments")


def seed_queues(db):
    """Create sample queues."""
    print("\n[5/6] Creating queues...")

    queues_data = [
        ("Registration Queue", "For new student registration", QueueType.REGISTRATION, 50),
        ("Payment Processing", "Payment processing queue", QueueType.PAYMENT, 30),
        ("Student Support", "General student support", QueueType.SUPPORT, 0),
    ]

    queues = []
    for name, desc, qtype, capacity in queues_data:
        queue = Queue(
            queue_name=name,
            description=desc,
            queue_type=qtype,
            max_capacity=capacity
        )
        db.add(queue)
        queues.append(queue)

    db.commit()
    print(f"✓ Created {len(queues)} queues")
    return queues


def seed_payments(db):
    """Create sample payments."""
    print("\n[6/9] Creating payments...")

    parents = db.query(Parent).all()
    courses = db.query(Course).limit(3).all()

    count = 0

    # Parent tuition payments (more realistic)
    payment_data = [
        (0, 0, Decimal("500.00"), PaymentMethod.CARD, "Payment for MATH101 - Fall semester"),
        (0, 1, Decimal("550.00"), PaymentMethod.CASH, "Payment for SCI101"),
        (1, 0, Decimal("500.00"), PaymentMethod.TRANSFER, "Tuition payment - MATH101"),
        (1, 2, Decimal("450.00"), PaymentMethod.CARD, "ENG101 course payment"),
        (2, 1, Decimal("550.00"), PaymentMethod.CARD, "Physics course fee"),
    ]

    for parent_idx, course_idx, amount, method, notes in payment_data:
        if parent_idx < len(parents) and course_idx < len(courses):
            payment = Payment(
                payer_id=parents[parent_idx].user_id,
                amount=amount,
                payment_type=PaymentType.TUITION,
                payment_method=method,
                payment_date=datetime.utcnow() - timedelta(days=30 - (count * 3)),
                status=PaymentStatus.COMPLETED,
                reference_id=courses[course_idx].id,
                notes=notes
            )
            db.add(payment)
            count += 1

    db.commit()
    print(f"✓ Created {count} payments")


def seed_expenses(db):
    """Create sample expenses."""
    print("\n[7/9] Creating expenses...")

    managers = db.query(Manager).all()
    manager_id = managers[0].user_id if managers else 1

    expenses_data = [
        (ExpenseCategory.SALARY, Decimal("15000.00"), date.today() - timedelta(days=30), "Monthly teacher salaries - October"),
        (ExpenseCategory.UTILITIES, Decimal("850.00"), date.today() - timedelta(days=25), "Electricity and water bill"),
        (ExpenseCategory.MAINTENANCE, Decimal("450.00"), date.today() - timedelta(days=20), "Repair broken chairs in classroom"),
        (ExpenseCategory.SUPPLIES, Decimal("320.00"), date.today() - timedelta(days=15), "Office supplies and stationery"),
        (ExpenseCategory.OTHER, Decimal("5000.00"), date.today() - timedelta(days=35), "Monthly facility rent"),
        (ExpenseCategory.OTHER, Decimal("1200.00"), date.today() - timedelta(days=40), "Business insurance premium"),
        (ExpenseCategory.OTHER, Decimal("500.00"), date.today() - timedelta(days=10), "Social media advertising"),
        (ExpenseCategory.SUPPLIES, Decimal("275.00"), date.today() - timedelta(days=5), "Teaching materials and books"),
    ]

    count = 0
    for category, amount, exp_date, description in expenses_data:
        expense = Expense(
            category=category,
            amount=amount,
            expense_date=exp_date,
            description=description,
            created_by_manager_id=manager_id
        )
        db.add(expense)
        count += 1

    db.commit()
    print(f"✓ Created {count} expenses")


def seed_maintenance_tasks(db):
    """Create sample maintenance tasks."""
    print("\n[8/9] Creating maintenance tasks...")

    workers = db.query(Worker).all()
    teachers = db.query(Teacher).all()
    managers = db.query(Manager).all()

    manager_id = managers[0].user_id if managers else 1
    teacher_id = teachers[0].user_id if teachers else 2
    worker1_id = workers[0].user_id if len(workers) > 0 else None
    worker2_id = workers[1].user_id if len(workers) > 1 else None

    tasks_data = [
        ("Fix broken chair in Room 101", "Chair leg is broken, needs repair or replacement", "Room 101",
         TaskPriority.MEDIUM, TaskStatus.COMPLETED, worker1_id, teacher_id,
         datetime.utcnow() - timedelta(days=10), datetime.utcnow() - timedelta(days=9), datetime.utcnow() - timedelta(days=7)),

        ("AC not working in Room 203", "Air conditioning unit not cooling properly", "Room 203",
         TaskPriority.HIGH, TaskStatus.IN_PROGRESS, worker1_id, manager_id,
         datetime.utcnow() - timedelta(days=3), datetime.utcnow() - timedelta(days=2), None),

        ("Replace broken window", "Window in hallway is cracked - safety hazard", "Main Hallway - 2nd Floor",
         TaskPriority.URGENT, TaskStatus.PENDING, None, worker2_id,
         datetime.utcnow() - timedelta(days=1), None, None),

        ("Paint classroom walls", "Room 105 walls need repainting", "Room 105",
         TaskPriority.LOW, TaskStatus.PENDING, worker2_id, manager_id,
         datetime.utcnow() - timedelta(days=5), None, None),

        ("Fix leaking faucet", "Bathroom faucet is leaking water", "Faculty Bathroom - 1st Floor",
         TaskPriority.MEDIUM, TaskStatus.IN_PROGRESS, worker1_id, teacher_id,
         datetime.utcnow() - timedelta(days=2), datetime.utcnow() - timedelta(days=1), None),
    ]

    count = 0
    for title, desc, location, priority, status, worker_id, reporter_id, created, started, completed in tasks_data:
        task = MaintenanceTask(
            title=title,
            description=desc,
            location=location,
            priority=priority,
            status=status,
            assigned_to_worker_id=worker_id,
            reported_by_user_id=reporter_id,
            created_at=created,
            started_at=started,
            completed_at=completed
        )
        db.add(task)
        count += 1

    db.commit()
    print(f"✓ Created {count} maintenance tasks")


def link_parent_students(db):
    """Link parents to students."""
    print("\n[9/9] Linking parents to students...")

    parents = db.query(Parent).all()
    students = db.query(Student).all()

    # Link students to parents
    if len(students) >= 10 and len(parents) >= 3:
        # Parent 1 -> Students 1-3
        for i in range(0, 3):
            students[i].parent_id = parents[0].user_id

        # Parent 2 -> Students 4-6
        for i in range(3, 6):
            students[i].parent_id = parents[1].user_id

        # Parent 3 -> Students 7-8
        for i in range(6, 8):
            students[i].parent_id = parents[2].user_id

    db.commit()
    print(f"✓ Linked students to parents")


def seed_database():
    """Main seeding function."""
    try:
        print("=" * 60)
        print("Database Seeding Script")
        print("=" * 60)

        with get_db_context() as db:
            users = seed_users(db)
            seed_role_profiles(db, users)
            courses = seed_courses(db)
            seed_enrollments(db, courses)
            queues = seed_queues(db)
            seed_payments(db)
            seed_expenses(db)
            seed_maintenance_tasks(db)
            link_parent_students(db)

        print("\n" + "=" * 60)
        print("Database seeding completed successfully!")
        print("=" * 60)
        print("\nDefault login credentials:")
        print("  Manager:  manager1 / password123")
        print("  Teacher:  teacher1 / password123")
        print("  Student:  student1 / password123")
        print("  Parent:   parent1  / password123")
        print("  Worker:   worker1  / password123")
        print("=" * 60)
        print("\nSample data includes:")
        print("  - 5 tuition payments from parents")
        print("  - 8 expense records (salary, utilities, maintenance, etc.)")
        print("  - 5 maintenance tasks (various priorities and statuses)")
        print("  - Student-parent relationships")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"\n✗ Error seeding database: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = seed_database()
    sys.exit(0 if success else 1)
