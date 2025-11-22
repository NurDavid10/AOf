"""
Database reset script.

This script combines initialization and seeding in one command.
It drops all tables, recreates them, and populates with dummy data.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from init_db import init_database
from seed_data import seed_database


def reset_database():
    """
    Reset the database completely.

    This function:
    1. Drops all existing tables
    2. Creates fresh tables
    3. Populates with dummy data

    Returns:
        bool: True if successful, False otherwise
    """
    print("=" * 60)
    print("DATABASE RESET SCRIPT")
    print("=" * 60)
    print("\nWARNING: This will delete all existing data!")
    print("=" * 60)

    # Initialize database (drop and create tables)
    print("\nStep 1: Initializing database...")
    if not init_database():
        print("\n✗ Database initialization failed!")
        return False

    # Seed database with dummy data
    print("\nStep 2: Seeding database with dummy data...")
    if not seed_database():
        print("\n✗ Database seeding failed!")
        return False

    print("\n" + "=" * 60)
    print("DATABASE RESET COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print("\nYou can now run the application with:")
    print("  uv run uvicorn app.main:app --reload")
    print("\nThen visit: http://localhost:8000")
    print("=" * 60)

    return True


if __name__ == "__main__":
    try:
        success = reset_database()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
