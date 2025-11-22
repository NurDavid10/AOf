"""
Database migration script to add location column to maintenance_tasks table.

This script adds the 'location' column to the maintenance_tasks table
in a backwards-compatible way. It can be run safely on existing databases.

Usage:
    python scripts/add_location_column.py
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.database import get_db_context


def add_location_column():
    """Add location column to maintenance_tasks table if it doesn't exist."""
    try:
        print("=" * 60)
        print("Database Migration: Add location column")
        print("=" * 60)

        with get_db_context() as db:
            # Check if column already exists
            check_query = text("""
                SELECT COUNT(*) as count
                FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'maintenance_tasks'
                AND COLUMN_NAME = 'location'
            """)

            result = db.execute(check_query).fetchone()

            if result and result[0] > 0:
                print("\n✓ Location column already exists. No migration needed.")
                return True

            # Add the column
            print("\n→ Adding 'location' column to maintenance_tasks table...")

            alter_query = text("""
                ALTER TABLE maintenance_tasks
                ADD COLUMN location VARCHAR(200) NULL
                AFTER description
            """)

            db.execute(alter_query)
            db.commit()

            print("✓ Location column added successfully!")

        print("\n" + "=" * 60)
        print("Migration completed successfully!")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"\n✗ Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = add_location_column()
    sys.exit(0 if success else 1)
