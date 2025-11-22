"""
Database initialization script.

This script creates all database tables from the ORM models.
It can be run multiple times safely (re-runnable).
"""

import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import engine, Base, drop_db
from app.models import (
    User, Manager, Teacher, Student, Parent, Worker,
    Course, CourseEnrollment,
    Task, TaskSubmission,
    Payment,
    Queue, QueueItem,
    Expense,
    MaintenanceTask
)


def init_database():
    """
    Initialize the database by creating all tables.

    This function:
    1. Drops all existing tables (for clean slate)
    2. Creates all tables defined in ORM models
    3. Sets up indexes and constraints

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        print("=" * 60)
        print("Database Initialization Script")
        print("=" * 60)

        # Drop all existing tables
        print("\n[1/2] Dropping existing tables...")
        drop_db()
        print("✓ All tables dropped successfully")

        # Create all tables
        print("\n[2/2] Creating tables...")
        Base.metadata.create_all(bind=engine)
        print("✓ All tables created successfully")

        # Print created tables
        print("\nCreated tables:")
        for table in Base.metadata.sorted_tables:
            print(f"  - {table.name}")

        print("\n" + "=" * 60)
        print("Database initialization completed successfully!")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"\n✗ Error initializing database: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1)
