# Academic Tomorrow Learning Center Management System

A comprehensive learning center management system built with Python, FastAPI, MySQL, and Tailwind CSS.

## Features

- **3-Layer Architecture**: Frontend (FastAPI + Jinja2), Business Logic (Services), Data Layer (SQLAlchemy + MySQL)
- **OOP Principles**: Inheritance, Polymorphism, and Encapsulation
- **Role-Based Access Control**: Manager, Teacher, Student, Parent, Worker
- **User Authentication**: Secure login with bcrypt password hashing
- **Course Management**: Create and manage courses with enrollments
- **Task System**: Assignments, exams, projects with submissions and grading
- **Payment Tracking**: Financial management and payment history
- **Queue Management**: Automated queue handling for various services
- **Responsive UI**: Tailwind CSS for modern, mobile-friendly interface

## Technology Stack

- **Language**: Python 3.13+
- **Package Manager**: uv
- **Web Framework**: FastAPI
- **Database**: MySQL
- **ORM**: SQLAlchemy
- **Frontend**: Jinja2 Templates + Tailwind CSS
- **Authentication**: bcrypt

## Prerequisites

Before you begin, ensure you have the following installed:

- Python 3.13 or higher
- MySQL 8.0 or higher
- uv package manager

## Installation

### 1. Install uv Package Manager

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Clone the Repository

```bash
cd academic_tomorrow  # Or wherever you cloned this project
```

### 3. Install Dependencies

```bash
uv sync
```

This will install all required dependencies listed in `pyproject.toml`.

### 4. Set Up MySQL Database

Open MySQL and create the database:

```bash
mysql -u root -p
```

Then in MySQL prompt:

```sql
CREATE DATABASE academic_tomorrow;
EXIT;
```

### 5. Configure Environment Variables

Copy the example environment file and configure it with your MySQL credentials:

```bash
cp .env.example .env
```

Edit `.env` file with your settings:

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=academic_tomorrow
SECRET_KEY=your-secret-key-here
```

**Important**: Replace `your_mysql_password` with your actual MySQL password and `your-secret-key-here` with a secure random string.

### 6. Initialize and Seed Database

Run the database reset script to create tables and populate with dummy data:

```bash
uv run python scripts/reset_db.py
```

This script will:
- Drop existing tables (if any)
- Create all necessary tables
- Populate the database with sample users, courses, and data

## Running the Application

Start the FastAPI development server:

```bash
uv run uvicorn app.main:app --reload
```

The application will be available at: **http://localhost:8000**

### Worker Access

Workers access all functionality through the web interface, consistent with other roles:
- **Dashboard**: `/worker/dashboard` - View task statistics and recent tasks
- **My Tasks**: `/worker/tasks` - View and manage assigned maintenance tasks
- **Report Issue**: `/worker/report-issue` - Report new maintenance issues

Worker functionality is implemented via `app/routers/worker_routes.py` and uses `MaintenanceService` for all business logic.

## Default Login Credentials

After seeding the database, you can log in with these demo accounts:

| Role | Username | Password |
|------|----------|----------|
| **Manager** | manager1 | password123 |
| **Teacher** | teacher1 | password123 |
| **Student** | student1 | password123 |
| **Parent** | parent1 | password123 |
| **Worker** | worker1 | password123 |

## Project Structure

```
academic_tomorrow/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration management
│   ├── database.py             # Database connection & session
│   ├── models/                 # Data Layer (ORM models)
│   │   ├── __init__.py
│   │   ├── base.py            # Base model classes
│   │   ├── user.py            # User hierarchy (inheritance)
│   │   ├── course.py          # Course models
│   │   ├── task.py            # Task & submission models
│   │   ├── payment.py         # Payment models
│   │   └── queue.py           # Queue models
│   ├── services/               # Business Logic Layer
│   │   ├── __init__.py
│   │   ├── auth_service.py    # Authentication & authorization
│   │   └── user_service.py    # User management logic
│   ├── schemas/                # Pydantic schemas for validation
│   │   ├── __init__.py
│   │   ├── user_schema.py
│   │   ├── course_schema.py
│   │   ├── task_schema.py
│   │   ├── payment_schema.py
│   │   └── queue_schema.py
│   ├── templates/              # HTML templates (Jinja2)
│   │   ├── base.html
│   │   ├── login.html
│   │   ├── manager/
│   │   ├── teacher/
│   │   ├── student/
│   │   ├── parent/
│   │   └── worker/
│   └── static/                 # Static files (CSS, JS)
│       ├── css/
│       └── js/
├── scripts/
│   ├── init_db.py             # Database initialization
│   ├── seed_data.py           # Dummy data generation
│   └── reset_db.py            # Complete database reset
├── docs/                       # Project documentation
│   ├── ticket-01/             # Core system architecture
│   ├── ticket-02/             # User, course & queue management
│   └── ticket-03/             # Financial & maintenance modules
├── .env.example               # Example environment variables
├── .env                       # Environment variables (not in git)
├── .gitignore                 # Git ignore rules
├── pyproject.toml             # Project dependencies
└── README.md                  # This file
```

## Architecture

### Three-Layer Architecture

```
┌─────────────────────────────────────┐
│     Frontend Layer (FastAPI)        │
│  - Web routes & templates           │
│  - Login & role-based routing       │
│  - Tailwind CSS UI                  │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│     Business Logic Layer            │
│  - Validations (unique username)    │
│  - Authentication & authorization   │
│  - Business rules & calculations    │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│     Data Layer (MySQL + ORM)        │
│  - Database schema & models         │
│  - CRUD operations                  │
│  - Relationships & constraints      │
└─────────────────────────────────────┘
```

### OOP Implementation

The project demonstrates key OOP principles:

1. **Inheritance**: User base class extended by Manager, Teacher, Student, Parent, Worker
2. **Polymorphism**: Override methods like `get_dashboard_route()`, `get_permissions()`, `can_access()`
3. **Encapsulation**: Properties with `@property` decorators, private attributes with `_` prefix

Example from `app/models/user.py`:

```python
class User(BaseModel):
    """Base User class"""
    # Common fields and methods

    def get_dashboard_route(self) -> str:
        """Polymorphic method"""
        return f"/{self.role.value}/dashboard"

class Manager(BaseModel):
    """Manager inherits common behavior"""

    def get_permissions(self) -> list[str]:
        """Override to provide manager-specific permissions"""
        return ["manage_users", "manage_courses", ...]
```

## Database Management

### Reset Database

To completely reset the database (drop, recreate, and seed):

```bash
uv run python scripts/reset_db.py
```

### Initialize Only (No Data)

To just create tables without dummy data:

```bash
uv run python scripts/init_db.py
```

### Seed Data Only

To add dummy data to an existing database:

```bash
uv run python scripts/seed_data.py
```

## Development

### Running in Development Mode

```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Options:
- `--reload`: Auto-reload on code changes
- `--host 0.0.0.0`: Listen on all network interfaces
- `--port 8000`: Specify port (default: 8000)

### Adding New Dependencies

```bash
uv add package-name
```

## Key Features Implementation

### 1. User Authentication
- Bcrypt password hashing (app/services/auth_service.py:29)
- Session-based authentication (app/main.py:71)
- Role-based access control (app/main.py:128)

### 2. Unique Username Validation
- Enforced at service layer (app/services/user_service.py:29)
- Database-level unique constraint

### 3. OOP Inheritance Hierarchy
- Base User class (app/models/user.py:48)
- Role-specific classes: Manager, Teacher, Student, Parent, Worker
- Polymorphic methods for role-specific behavior

### 4. Error Handling
- Try/except blocks throughout services
- User-friendly error messages
- Database transaction management

## Troubleshooting

### Database Connection Issues

If you encounter database connection errors:

1. Verify MySQL is running:
   ```bash
   mysql --version
   ```

2. Check credentials in `.env` file

3. Ensure database exists:
   ```sql
   SHOW DATABASES;
   ```

### Import Errors

If you get module import errors:

```bash
# Reinstall dependencies
uv sync
```

### Port Already in Use

If port 8000 is already in use:

```bash
# Use a different port
uv run uvicorn app.main:app --reload --port 8001
```

## API Documentation

Once the application is running, visit:

- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative API Docs**: http://localhost:8000/redoc

## Security Notes

- **Never commit `.env` file** - It contains sensitive credentials
- **Change SECRET_KEY** - Use a strong, random secret key in production
- **Use strong passwords** - Default passwords are for demo only
- **Enable HTTPS** - In production, always use HTTPS

## License

This project is for educational purposes as part of the Academic Tomorrow Learning Center system.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the project documentation in `/docs`
3. Check MySQL and Python logs for error details

---

**Built with Python, FastAPI, MySQL, and Tailwind CSS**
