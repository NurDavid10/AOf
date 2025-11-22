# Academic Tomorrow - Learning Center Management System
## Comprehensive Project Plan

---

## 1. Project Overview

### 1.1 System Description
A full-stack web application for managing a learning center with role-based access control, course management, enrollment queuing, financial tracking, and facility maintenance.

### 1.2 Core Objectives
- Implement 3-layer architecture (Data, Business Logic, Frontend)
- Build complete OOP system with inheritance and polymorphism
- Create web-based UI with role-specific dashboards
- Implement automated queue management system
- Track finances and maintenance tasks
- Generate comprehensive reports

### 1.3 User Roles
1. **Manager**: Full system access, user/course creation, reports
2. **Parent**: Enroll children, view progress, make payments
3. **Teacher**: View assigned courses, manage grades, report issues
4. **Student**: View schedule and grades
5. **Worker**: View and update maintenance tasks

---

## 2. Technology Stack Recommendations

### 2.1 Backend Options
**Option A (Recommended for Learning):**
- **Framework**: Flask 3.x
- **Database**: PostgreSQL or MySQL
- **ORM**: SQLAlchemy
- **Authentication**: Flask-Login (session-based)
- **Forms**: Flask-WTF
- **Migration**: Alembic

**Option B (Modern/Scalable):**
- **Framework**: FastAPI
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy 2.0
- **Authentication**: JWT with python-jose
- **Validation**: Pydantic
- **Migration**: Alembic

### 2.2 Frontend
- **Templates**: Jinja2
- **CSS Framework**: Bootstrap 5
- **JavaScript**: Vanilla JS or Alpine.js (lightweight)
- **Icons**: Bootstrap Icons or Font Awesome
- **Charts**: Chart.js for dashboards

### 2.3 Database
- **Primary**: PostgreSQL (production) or SQLite (development)
- **Connection Pool**: SQLAlchemy engine with pool management
- **Migration Tool**: Alembic

---

## 3. System Architecture

### 3.1 Three-Layer Architecture

```
┌─────────────────────────────────────────────┐
│         PRESENTATION LAYER (Frontend)       │
│  - Flask/FastAPI Routes                     │
│  - Jinja2 Templates                         │
│  - Forms & Validation                       │
│  - Role-based access control                │
└─────────────────────────────────────────────┘
                    ↕
┌─────────────────────────────────────────────┐
│       BUSINESS LOGIC LAYER (Services)       │
│  - UserService                              │
│  - CourseService                            │
│  - EnrollmentService                        │
│  - QueueService (auto-management)           │
│  - PaymentService                           │
│  - MaintenanceService                       │
│  - ReportService                            │
└─────────────────────────────────────────────┘
                    ↕
┌─────────────────────────────────────────────┐
│         DATA LAYER (Repository/DAO)         │
│  - Database Models (SQLAlchemy)             │
│  - CRUD Operations                          │
│  - Query Methods                            │
│  - Transaction Management                   │
└─────────────────────────────────────────────┘
                    ↕
┌─────────────────────────────────────────────┐
│              DATABASE (RDBMS)               │
│  - PostgreSQL / MySQL / SQLite              │
└─────────────────────────────────────────────┘
```

---

## 4. Database Schema Design

### 4.1 Core Tables

#### Users Table
```sql
users
- id (PK, AUTO_INCREMENT)
- username (UNIQUE, NOT NULL)
- email (UNIQUE, NOT NULL)
- password_hash (NOT NULL)
- first_name (NOT NULL)
- last_name (NOT NULL)
- user_type (ENUM: manager, parent, teacher, student, worker)
- phone
- address
- is_active (BOOLEAN, DEFAULT TRUE)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)
```

#### Parent-Student Relationship
```sql
parent_student
- id (PK)
- parent_id (FK → users.id)
- student_id (FK → users.id)
- relationship (e.g., 'father', 'mother', 'guardian')
- created_at
```

#### Courses Table
```sql
courses
- id (PK)
- name (NOT NULL)
- description
- teacher_id (FK → users.id)
- capacity (INT, NOT NULL)
- current_enrollment (INT, DEFAULT 0)
- price (DECIMAL)
- schedule (TEXT/JSON)
- start_date (DATE)
- end_date (DATE)
- is_active (BOOLEAN, DEFAULT TRUE)
- created_at
- updated_at
```

#### Enrollments Table
```sql
enrollments
- id (PK)
- student_id (FK → users.id)
- course_id (FK → courses.id)
- enrolled_by_parent_id (FK → users.id)
- enrollment_date (TIMESTAMP)
- status (ENUM: active, completed, dropped, pending)
- final_grade (DECIMAL, NULL)
- created_at
- updated_at
```

#### Queue Table (Waiting List)
```sql
course_queue
- id (PK)
- student_id (FK → users.id)
- course_id (FK → courses.id)
- parent_id (FK → users.id)
- queue_position (INT)
- requested_at (TIMESTAMP)
- notified (BOOLEAN, DEFAULT FALSE)
- status (ENUM: waiting, enrolled, expired)
- created_at
- updated_at
```

#### Payments Table
```sql
payments
- id (PK)
- parent_id (FK → users.id)
- student_id (FK → users.id)
- course_id (FK → courses.id)
- amount (DECIMAL, NOT NULL)
- payment_date (DATE, NOT NULL)
- payment_method (ENUM: cash, card, transfer)
- receipt_number (UNIQUE)
- notes
- created_at
```

#### Expenses Table
```sql
expenses
- id (PK)
- category (e.g., 'salary', 'maintenance', 'utilities', 'supplies')
- amount (DECIMAL, NOT NULL)
- expense_date (DATE, NOT NULL)
- description
- created_by_manager_id (FK → users.id)
- created_at
```

#### Maintenance Tasks Table
```sql
maintenance_tasks
- id (PK)
- title (NOT NULL)
- description (TEXT)
- priority (ENUM: low, medium, high, urgent)
- status (ENUM: pending, in_progress, completed, cancelled)
- assigned_to_worker_id (FK → users.id, NULL)
- reported_by_user_id (FK → users.id)
- created_at
- started_at (TIMESTAMP, NULL)
- completed_at (TIMESTAMP, NULL)
- notes (TEXT)
```

#### Grades Table
```sql
grades
- id (PK)
- enrollment_id (FK → enrollments.id)
- assignment_name (NOT NULL)
- score (DECIMAL)
- max_score (DECIMAL)
- grade_date (DATE)
- comments (TEXT)
- created_by_teacher_id (FK → users.id)
- created_at
```

---

## 5. Object-Oriented Design

### 5.1 Class Hierarchy

```python
Base Class: User (Abstract)
├── Manager
├── Parent
├── Teacher
├── Student
└── Worker
```

### 5.2 Core Classes with Methods

#### User (Base Class)
```python
class User:
    # Attributes
    - id
    - username
    - email
    - password_hash
    - first_name
    - last_name
    - user_type
    - phone
    - address
    - is_active

    # Methods (to be overridden)
    + authenticate(password)
    + get_dashboard_data()  # Polymorphic
    + get_permissions()     # Polymorphic
    + __str__()
```

#### Manager (extends User)
```python
class Manager(User):
    + get_dashboard_data()  # Returns: users count, courses, queue summary, budget
    + get_permissions()     # Full access
    + create_user(user_data)
    + create_course(course_data)
    + view_financial_report(start_date, end_date)
    + view_maintenance_tasks()
    + assign_maintenance_task(task_id, worker_id)
    + get_queue_suggestions()  # ≥5 students → suggest new class
```

#### Parent (extends User)
```python
class Parent(User):
    + get_children()
    + get_dashboard_data()  # Returns: children's courses, payments, queue status
    + enroll_child(student_id, course_id)
    + view_child_grades(student_id)
    + view_queue_position(student_id, course_id)
    + make_payment(student_id, course_id, amount)
    + view_payment_history()
```

#### Teacher (extends User)
```python
class Teacher(User):
    + get_assigned_courses()
    + get_dashboard_data()  # Returns: assigned courses, students
    + view_course_students(course_id)
    + assign_grade(enrollment_id, grade_data)
    + report_maintenance_issue(issue_data)
```

#### Student (extends User)
```python
class Student(User):
    + get_enrolled_courses()
    + get_dashboard_data()  # Returns: schedule, grades
    + view_schedule()
    + view_grades()
```

#### Worker (extends User)
```python
class Worker(User):
    + get_assigned_tasks()
    + get_dashboard_data()  # Returns: assigned tasks by status
    + update_task_status(task_id, new_status)
    + report_maintenance_issue(issue_data)
```

### 5.3 Service Layer Classes

```python
class UserService:
    + create_user(user_data, created_by_manager)
    + authenticate_user(username, password)
    + get_user_by_id(user_id)
    + update_user(user_id, user_data)
    + delete_user(user_id)
    + validate_unique_username(username)
    + validate_unique_email(email)

class CourseService:
    + create_course(course_data, created_by_manager)
    + update_course(course_id, course_data)
    + get_course_by_id(course_id)
    + get_all_courses(filters)
    + get_available_slots(course_id)
    + is_course_full(course_id)

class EnrollmentService:
    + enroll_student(student_id, course_id, parent_id)
    + drop_student(enrollment_id)
    + get_student_enrollments(student_id)
    + get_course_enrollments(course_id)

class QueueService:
    + add_to_queue(student_id, course_id, parent_id)
    + remove_from_queue(queue_id)
    + get_queue_position(student_id, course_id)
    + process_queue_on_vacancy(course_id)  # Auto-enroll next student
    + get_queue_suggestions()  # ≥5 students waiting
    + notify_queue_advancement(queue_id)

class PaymentService:
    + record_payment(payment_data)
    + get_parent_payment_history(parent_id)
    + get_financial_report(start_date, end_date)
    + calculate_total_income(start_date, end_date)
    + calculate_total_expenses(start_date, end_date)
    + calculate_net_result(start_date, end_date)

class MaintenanceService:
    + create_task(task_data)
    + assign_task(task_id, worker_id, assigned_by_manager)
    + update_task_status(task_id, new_status, updated_by_user)
    + get_tasks_by_status(status)
    + get_worker_tasks(worker_id)
    + get_open_tasks_count()

class ReportService:
    + generate_manager_dashboard()
    + generate_parent_dashboard(parent_id)
    + generate_teacher_dashboard(teacher_id)
    + generate_worker_dashboard(worker_id)
    + get_students_per_course()
    + get_queue_summary()
```

---

## 6. Frontend Structure

### 6.1 Page Organization

```
templates/
├── base.html                    # Base template with nav
├── auth/
│   ├── login.html              # Login page
│   └── register.html           # Optional self-registration
├── manager/
│   ├── dashboard.html          # Manager overview
│   ├── users_list.html         # View/manage users
│   ├── user_create.html        # Create user form
│   ├── courses_list.html       # View/manage courses
│   ├── course_create.html      # Create course form
│   ├── queues.html             # View all queues
│   ├── financial_report.html   # Income/expense report
│   └── maintenance_tasks.html  # View/assign tasks
├── parent/
│   ├── dashboard.html          # Parent overview
│   ├── enroll_child.html       # Enrollment form
│   ├── child_grades.html       # View child grades
│   ├── queue_status.html       # View queue positions
│   ├── make_payment.html       # Payment form
│   └── payment_history.html    # View payments
├── teacher/
│   ├── dashboard.html          # Teacher overview
│   ├── courses.html            # View assigned courses
│   ├── students.html           # View course students
│   ├── assign_grades.html      # Grade entry form
│   └── report_issue.html       # Maintenance report form
├── student/
│   ├── dashboard.html          # Student overview
│   ├── schedule.html           # View schedule
│   └── grades.html             # View grades
└── worker/
    ├── dashboard.html          # Worker overview
    ├── tasks.html              # View assigned tasks
    └── report_issue.html       # Maintenance report form
```

### 6.2 Common UI Components
- Navigation bar (role-based menu items)
- Data tables with sorting/pagination
- Form validation (client + server side)
- Success/error flash messages
- Modals for confirmations
- Charts for dashboard visualizations

---

## 7. Implementation Plan (Phased Approach)

### Phase 1: Foundation & Infrastructure (Ticket 1)
**Duration**: ~3-5 days

#### Tasks:
1. **Project Setup**
   - Initialize project structure
   - Set up virtual environment
   - Install dependencies (Flask/FastAPI, SQLAlchemy, etc.)
   - Configure database connection
   - Set up environment variables (.env file)

2. **Data Layer Implementation**
   - Create database models (SQLAlchemy)
   - Implement User base class and subclasses
   - Create other models (Course, Enrollment, Queue, Payment, etc.)
   - Set up Alembic for migrations
   - Create initial migration script
   - Write database initialization script with dummy data

3. **Business Logic Layer - Part 1**
   - Implement UserService (CRUD, authentication)
   - Add username/email uniqueness validation
   - Implement password hashing (bcrypt)
   - Add error handling and logging

4. **Frontend Layer - Basic**
   - Set up Flask/FastAPI app structure
   - Create base template with Bootstrap
   - Implement login system
   - Create role-based routing/decorators
   - Implement session management
   - Create basic dashboard for each role (placeholder)

5. **Testing & Documentation**
   - Test database connection and CRUD
   - Test login flow
   - Write README with setup instructions
   - Document database configuration
   - Add docstrings to all classes/methods

#### Deliverables:
- Running web application with login
- Database schema created
- Role-based routing works
- README with setup guide

---

### Phase 2: Core Business Logic (Ticket 2)
**Duration**: ~4-6 days

#### Tasks:
1. **User Management**
   - Manager: Create user form and logic
   - Manager: View users list
   - Manager: Edit/deactivate users
   - Frontend: User management UI

2. **Course Management**
   - Manager: Create course form
   - Manager: View courses list
   - Manager: Edit course details
   - Implement capacity tracking
   - Frontend: Course management UI

3. **Enrollment & Queue System**
   - CourseService: Check capacity logic
   - EnrollmentService: Enroll student
   - QueueService: Add to waiting list when full
   - QueueService: Auto-promotion when slot opens
   - Parent: Enroll child UI
   - Parent: View enrollment status

4. **Queue Monitoring**
   - Parent: View child's queue position
   - Manager: View all course queues
   - Manager: Queue suggestions (≥5 students)
   - Frontend: Queue visualization

5. **Teacher & Student Features**
   - Teacher: View assigned courses
   - Teacher: View course students
   - Teacher: Grade entry form
   - Student: View schedule
   - Student: View grades

6. **Testing**
   - Test enrollment flow
   - Test queue auto-promotion
   - Test queue position updates
   - Test role-based access

#### Deliverables:
- Complete user/course CRUD
- Working enrollment system
- Automated queue management
- Role-specific dashboards functional

---

### Phase 3: Financial, Maintenance & Reports (Ticket 3)
**Duration**: ~3-5 days

#### Tasks:
1. **Financial Tracking**
   - Payment model and service
   - Expense model and service
   - Parent: Record payment UI
   - Parent: View payment history
   - Manager: Income/expense report
   - Manager: Net result calculation
   - Frontend: Financial dashboard

2. **Maintenance Tasks**
   - MaintenanceTask model and service
   - Manager: Create task
   - Manager: Assign task to worker
   - Worker: View assigned tasks
   - Worker: Update task status
   - Teacher/Worker: Report new issue
   - Frontend: Maintenance UI

3. **Comprehensive Dashboards**
   - Manager dashboard:
     - Students per course chart
     - Queue summary table
     - Open tasks count
     - Budget summary (income/expense/net)
   - Parent dashboard:
     - Children's courses and grades
     - Payment history
     - Queue status
   - Worker dashboard:
     - Tasks by status
     - Task details

4. **Reports & Analytics**
   - ReportService implementation
   - Export functionality (CSV/PDF optional)
   - Chart visualizations (Chart.js)

5. **Final Polish**
   - UI/UX improvements
   - Form validation refinements
   - Error handling review
   - Performance optimization
   - Security audit

6. **Comprehensive Testing**
   - End-to-end testing all workflows
   - Test all role permissions
   - Test data integrity
   - Load testing (optional)

#### Deliverables:
- Complete financial module
- Complete maintenance module
- Comprehensive dashboards for all roles
- Full system functionality

---

## 8. Key Features Implementation Details

### 8.1 Queue Auto-Management Algorithm

```python
def process_queue_on_vacancy(course_id):
    """
    Called when:
    - Student drops from course
    - Course capacity increases
    """
    # 1. Check if course has available slots
    course = get_course_by_id(course_id)
    available_slots = course.capacity - course.current_enrollment

    if available_slots > 0:
        # 2. Get next student(s) in queue (ordered by requested_at)
        queue_entries = get_queue_entries(course_id, status='waiting',
                                          limit=available_slots)

        # 3. Enroll each student automatically
        for entry in queue_entries:
            try:
                enroll_student(entry.student_id, course_id, entry.parent_id)
                entry.status = 'enrolled'
                entry.notified = True
                # Send notification to parent (email/SMS)
                send_notification(entry.parent_id,
                                 f"Your child has been enrolled in {course.name}")
            except Exception as e:
                log_error(f"Failed to auto-enroll student {entry.student_id}: {e}")
```

### 8.2 Queue Suggestion System

```python
def get_queue_suggestions():
    """
    Returns courses with ≥5 students waiting
    Suggests opening new class sections
    """
    suggestions = []
    courses = get_all_courses()

    for course in courses:
        waiting_count = count_queue_entries(course.id, status='waiting')
        if waiting_count >= 5:
            suggestions.append({
                'course': course,
                'waiting_count': waiting_count,
                'suggestion': f"Consider opening a new section for {course.name}"
            })

    return suggestions
```

### 8.3 Role-Based Access Control

```python
# Decorator example (Flask)
def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login'))
            if current_user.user_type not in roles:
                abort(403)  # Forbidden
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Usage:
@app.route('/manager/dashboard')
@role_required('manager')
def manager_dashboard():
    # Only managers can access
    pass
```

---

## 9. Testing Strategy

### 9.1 Unit Tests
- Test each service method independently
- Mock database calls
- Test validation logic
- Test business rules (e.g., queue advancement)

### 9.2 Integration Tests
- Test layer interactions (Frontend → Business → Data)
- Test database transactions
- Test authentication flow

### 9.3 End-to-End Tests
- Test complete user workflows:
  - Manager creates course → Parent enrolls child
  - Course fills → Next student queued → Student drops → Queue auto-enrolls
  - Payment recorded → Financial report reflects it

### 9.4 Manual Testing Checklist
- [ ] Login with each role type
- [ ] Manager: Create user of each type
- [ ] Manager: Create course
- [ ] Parent: Enroll child (available slot)
- [ ] Parent: Enroll child (full course → queue)
- [ ] Parent: View queue position
- [ ] Manager: View queue suggestions
- [ ] Teacher: Assign grade
- [ ] Student: View grade
- [ ] Parent: Record payment
- [ ] Manager: View financial report
- [ ] Manager: Create maintenance task
- [ ] Manager: Assign task to worker
- [ ] Worker: Update task status
- [ ] All dashboards load correctly

---

## 10. Database Initialization

### 10.1 Dummy Data Script

Create a script `init_db.py` that:
1. Drops all tables (if exist)
2. Creates all tables from models
3. Inserts dummy data:
   - 1 Manager account
   - 2 Teacher accounts
   - 3 Parent accounts
   - 6 Student accounts (2 per parent)
   - 2 Worker accounts
   - 5 Courses (varying capacity)
   - Initial enrollments (some courses near full)
   - Queue entries (2-3 students waiting)
   - Payment records
   - Maintenance tasks (various statuses)

### 10.2 Default Credentials
```
Manager: username=admin, password=admin123
Teacher1: username=teacher1, password=teacher123
Parent1: username=parent1, password=parent123
Student1: username=student1, password=student123
Worker1: username=worker1, password=worker123
```

---

## 11. Project Structure

```
academic-tomorrow/
├── app/
│   ├── __init__.py              # App factory
│   ├── config.py                # Configuration
│   ├── models/                  # Data Layer
│   │   ├── __init__.py
│   │   ├── user.py              # User + subclasses
│   │   ├── course.py
│   │   ├── enrollment.py
│   │   ├── queue.py
│   │   ├── payment.py
│   │   ├── expense.py
│   │   ├── maintenance.py
│   │   └── grade.py
│   ├── services/                # Business Logic Layer
│   │   ├── __init__.py
│   │   ├── user_service.py
│   │   ├── course_service.py
│   │   ├── enrollment_service.py
│   │   ├── queue_service.py
│   │   ├── payment_service.py
│   │   ├── maintenance_service.py
│   │   └── report_service.py
│   ├── routes/                  # Frontend Layer (Controllers)
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── manager.py
│   │   ├── parent.py
│   │   ├── teacher.py
│   │   ├── student.py
│   │   └── worker.py
│   ├── templates/               # HTML templates
│   │   └── (as outlined in section 6.1)
│   ├── static/                  # CSS, JS, images
│   │   ├── css/
│   │   ├── js/
│   │   └── img/
│   └── utils/                   # Helpers
│       ├── decorators.py        # @role_required
│       ├── validators.py
│       └── notifications.py
├── migrations/                  # Alembic migrations
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── docs/
│   ├── ticket-01/
│   ├── ticket-02/
│   ├── ticket-03/
│   ├── TECHNICAL_GUIDE.md
│   └── API_DOCUMENTATION.md
├── scripts/
│   ├── init_db.py              # Database initialization
│   └── seed_data.py            # Dummy data
├── .env.example                # Environment variables template
├── requirements.txt            # Python dependencies
├── README.md                   # Setup and run instructions
└── run.py                      # Application entry point
```

---

## 12. Requirements File (requirements.txt)

```
# Web Framework (choose one)
Flask==3.0.0
Flask-SQLAlchemy==3.1.1
Flask-Login==0.6.3
Flask-WTF==1.2.1
# OR
# fastapi==0.104.1
# uvicorn==0.24.0

# Database
SQLAlchemy==2.0.23
alembic==1.13.0
psycopg2-binary==2.9.9  # PostgreSQL
# OR
# PyMySQL==1.1.0  # MySQL
# OR for SQLite, no additional driver needed

# Security
bcrypt==4.1.1
python-dotenv==1.0.0

# Forms & Validation
WTForms==3.1.1
email-validator==2.1.0

# Optional
python-dateutil==2.8.2
```

---

## 13. Security Considerations

### 13.1 Authentication & Authorization
- Hash passwords with bcrypt (never store plaintext)
- Use secure session management
- Implement CSRF protection (Flask-WTF)
- Validate all inputs (server-side)
- Implement role-based access control (decorators)

### 13.2 Database Security
- Use parameterized queries (SQLAlchemy ORM handles this)
- Implement database user with minimal privileges
- Never commit .env file with credentials
- Use connection pooling properly

### 13.3 Input Validation
- Validate all form inputs
- Sanitize HTML output (Jinja2 auto-escapes)
- Validate file uploads (if implemented)
- Limit request sizes

### 13.4 Error Handling
- Never expose stack traces to users
- Log errors securely
- Use generic error messages for security issues
- Implement rate limiting (optional)

---

## 14. Documentation Requirements

### 14.1 README.md
Must include:
- Project description
- Features list
- Technology stack
- Prerequisites (Python version, database)
- Installation steps
- Database setup (create DB, configure credentials)
- How to run (development server)
- Default login credentials
- Project structure overview

### 14.2 TECHNICAL_GUIDE.md
Must include:
- Architecture explanation (3 layers)
- Class diagrams
- Database schema diagram
- API endpoints (if applicable)
- Service layer documentation
- How to extend/modify

### 14.3 Code Documentation
- Docstrings for all classes
- Docstrings for all methods
- Inline comments for complex logic
- Type hints (Python 3.10+)

---

## 15. Deployment Considerations (Optional/Future)

### 15.1 Production Checklist
- [ ] Use production WSGI server (Gunicorn)
- [ ] Set up Nginx reverse proxy
- [ ] Enable HTTPS (SSL certificate)
- [ ] Use production database (PostgreSQL)
- [ ] Set DEBUG=False
- [ ] Implement proper logging
- [ ] Set up database backups
- [ ] Configure environment variables securely
- [ ] Implement monitoring (optional)

### 15.2 Environment Variables (.env)
```
# Flask
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=academic_tomorrow
DB_USER=your_db_user
DB_PASSWORD=your_db_password

# Optional
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
```

---

## 16. Success Criteria & Validation

### 16.1 Ticket 1 Completion Criteria
- [x] Database schema created and initialized
- [x] User class hierarchy implemented with OOP principles
- [x] 3-layer architecture in place
- [x] Web application running with login
- [x] Role-based routing works
- [x] README and technical documentation complete

### 16.2 Ticket 2 Completion Criteria
- [x] Manager can create users of all roles
- [x] Manager can create/edit courses
- [x] Parent can enroll children
- [x] Queue system auto-enrolls when slot opens
- [x] Queue position visible to parents
- [x] Queue suggestions (≥5 waiting) shown to manager
- [x] Teacher can assign grades
- [x] Student can view schedule and grades
- [x] All features accessible via web UI

### 16.3 Ticket 3 Completion Criteria
- [x] Parent can record payments
- [x] Manager can view financial reports (income/expense/net)
- [x] Manager can create and assign maintenance tasks
- [x] Worker can update task status
- [x] Teacher/Worker can report issues
- [x] Manager dashboard shows all key metrics
- [x] Parent dashboard shows child progress and payments
- [x] Worker dashboard shows assigned tasks
- [x] System meets all OOP, 3-layer, and web UI requirements

---

## 17. Timeline Summary

| Phase | Focus | Duration | Tickets |
|-------|-------|----------|---------|
| Phase 1 | Foundation & Architecture | 3-5 days | Ticket 1 |
| Phase 2 | Core Business Logic | 4-6 days | Ticket 2 |
| Phase 3 | Financial, Maintenance & Reports | 3-5 days | Ticket 3 |
| **Total** | | **10-16 days** | All |

---

## 18. Risk Management

### 18.1 Technical Risks
| Risk | Impact | Mitigation |
|------|--------|------------|
| Database connection issues | High | Provide clear setup guide, test scripts |
| OOP complexity | Medium | Create clear class diagrams, document inheritance |
| Queue auto-enrollment bugs | High | Extensive testing, transaction management |
| Session management issues | Medium | Use established libraries (Flask-Login) |

### 18.2 Project Risks
| Risk | Impact | Mitigation |
|------|--------|------------|
| Scope creep | Medium | Stick to ticket requirements, phase deliverables |
| Time estimation | Medium | Build in buffer time, prioritize core features |
| Testing gaps | High | Create comprehensive test checklist |

---

## 19. Next Steps

### Immediate Actions:
1. **Clarify Technology Choices** (address questions above)
2. **Set Up Development Environment**
   - Install Python, database, IDE
   - Create virtual environment
3. **Initialize Git Repository**
   - Create .gitignore (include .env, __pycache__, etc.)
4. **Begin Phase 1 Implementation**
   - Follow the implementation plan step-by-step

### Questions to Address Before Starting:
- [ ] Database choice confirmed (PostgreSQL/MySQL/SQLite)?
- [ ] Web framework confirmed (Flask/FastAPI)?
- [ ] Frontend complexity level confirmed?
- [ ] Authentication method confirmed?
- [ ] Any additional requirements or constraints?

---

## 20. Resources & References

### Documentation:
- Flask: https://flask.palletsprojects.com/
- FastAPI: https://fastapi.tiangolo.com/
- SQLAlchemy: https://docs.sqlalchemy.org/
- Bootstrap: https://getbootstrap.com/docs/

### Tutorials:
- Flask Mega-Tutorial: https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world
- SQLAlchemy ORM Tutorial: https://docs.sqlalchemy.org/en/20/orm/tutorial.html

---

**End of Project Plan**

*This plan should be reviewed and adjusted based on:*
- *Confirmed technology choices*
- *Team size and skill level*
- *Project timeline constraints*
- *Any additional requirements discovered during implementation*
