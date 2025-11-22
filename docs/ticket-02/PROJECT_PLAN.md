# Ticket-02 Project Plan: User, Course & Queue Management

## Overview
**Type:** Story
**Dependencies:** Ticket-01 (Core System Architecture)
**Goal:** Implement full-stack user, course, and queue management functionalities for all roles

---

## Prerequisites (from Ticket-01)
- ✓ 3-layer architecture (Data, Business Logic, Frontend)
- ✓ OOP user hierarchy (User → Manager/Parent/Teacher/Student/Worker)
- ✓ Database schema with CRUD operations
- ✓ Web application (Flask/FastAPI) with authentication
- ✓ Role-based routing

---

## Architecture Overview

### Data Layer Extensions
- User CRUD operations (all roles)
- Course CRUD operations with day schedule
- Enrollment and waitlist management
- Queue position tracking
- Auto-enrollment triggers
- Grade management (per student per course)
- Parent-child relationship management
- In-app notification system

### Business Logic Layer
- User creation with role-specific validations
- Parent-child linking (Parent manages own children)
- Course capacity and schedule management
- Enrollment business rules
- Queue advancement algorithm
- In-app notification system for queue updates
- Manager suggestion system (≥5 students waiting)
- Grade CRUD for teachers

### Frontend Layer (Web UI)
- Manager dashboard
- Parent dashboard
- Teacher dashboard
- Student dashboard
- Role-based forms and tables

---

## Implementation Tasks

### Phase 1: Data Layer Enhancements

#### 1.1 User Management Schema
- **Task:** Extend user tables/models to support full CRUD
- **Details:**
  - Ensure all role types (Manager, Parent, Teacher, Student, Worker) can be created
  - Add parent-child relationship table/field (many-to-many: one Parent can have multiple Students)
  - Create indexes for performance (username, email, role)
- **Parent-Child Relationship:**
  - `parent_student` table with `parent_id` (FK), `student_id` (FK)
  - Parents link children to their own account (not Manager)
- **Validation:**
  - Unique username constraint
  - Unique email constraint
  - Valid role enum
  - Parent-child relationship integrity (parent must have Parent role, student must have Student role)

#### 1.2 Course Management Schema
- **Task:** Implement course table/model
- **Fields:**
  - `course_id` (PK)
  - `name`
  - `teacher_id` (FK to User)
  - `capacity` (integer)
  - `price` (decimal) - **display only, no payment processing**
  - `day` (string/enum: e.g., "Monday", "Tuesday", etc.)
  - `current_enrollment` (integer, calculated)
  - `created_at`, `updated_at`
- **Relationships:**
  - Course → Teacher (many-to-one)
- **Methods:**
  - `create_course()`
  - `update_course()` - Manager can edit/update courses
  - `delete_course()` - Manager can delete courses
  - `get_course_by_id()`
  - `get_all_courses()`
  - `get_courses_by_teacher()`

#### 1.3 Enrollment & Queue Schema
- **Task:** Create enrollment and waitlist tables
- **Enrollment Table:**
  - `enrollment_id` (PK)
  - `student_id` (FK)
  - `course_id` (FK)
  - `enrolled_at` (timestamp)
  - `status` (enrolled/dropped)
- **Waitlist Table:**
  - `waitlist_id` (PK)
  - `student_id` (FK)
  - `course_id` (FK)
  - `position` (integer)
  - `joined_at` (timestamp)
  - `notified` (boolean) - for in-app notifications
- **Methods:**
  - `enroll_student()`
  - `add_to_waitlist()`
  - `remove_from_waitlist()`
  - `get_queue_position()`
  - `get_next_in_queue()`
  - `get_waitlist_by_course()`

#### 1.4 Grade Schema
- **Task:** Create grade table for teacher grade management
- **Grade Table:**
  - `grade_id` (PK)
  - `student_id` (FK)
  - `course_id` (FK)
  - `teacher_id` (FK) - teacher who assigned the grade
  - `grade` (string/decimal: e.g., "A", "B+", or numeric 85.5)
  - `comments` (text, optional)
  - `created_at`, `updated_at`
- **Validation:**
  - Unique constraint on (student_id, course_id) - one grade per student per course
  - Student must be enrolled in the course
  - Teacher must be the course instructor
- **Methods:**
  - `create_grade()`
  - `update_grade()` - Teachers can update grades
  - `get_grade_by_student_course()`
  - `get_grades_by_course()`
  - `get_grades_by_student()`

#### 1.5 Notification Schema
- **Task:** Create in-app notification table
- **Notification Table:**
  - `notification_id` (PK)
  - `user_id` (FK) - recipient
  - `message` (text)
  - `type` (string: 'queue_advance', 'enrollment_success', etc.)
  - `read` (boolean, default false)
  - `created_at`
- **Methods:**
  - `create_notification()`
  - `get_unread_notifications(user_id)`
  - `mark_as_read(notification_id)`
  - `get_all_notifications(user_id)`

---

### Phase 2: Business Logic Layer

#### 2.1 User Management Service
- **Task:** Implement user creation and management for Manager role
- **Features:**
  - `create_user(role, username, password, **kwargs)` - Manager only
  - `update_user()` - Manager can edit user details
  - `delete_user()` - Manager can delete users
  - Validate unique username
  - Hash passwords securely
  - Role-specific field validation
  - **Worker role:** Can be created but has no specific functionality in this ticket
- **Error Handling:**
  - Duplicate username
  - Invalid role
  - Missing required fields
  - Unauthorized access (non-Manager trying to create users)

#### 2.2 Parent-Child Management Service
- **Task:** Implement parent-child linking functionality
- **Features:**
  - `link_child(parent_id, student_id)` - Parent can link children to their account
  - `unlink_child(parent_id, student_id)` - Parent can remove child link
  - `get_children(parent_id)` - Get all children for a parent
  - Validate parent has Parent role and student has Student role
- **Error Handling:**
  - Invalid parent or student role
  - Child already linked to this parent
  - Unauthorized (only the parent can manage their own children)

#### 2.3 Course Management Service
- **Task:** Implement course CRUD for Manager role
- **Features:**
  - `create_course(name, teacher_id, capacity, price, day)` - Manager only
  - `update_course()` - Manager can edit all course details including capacity and day
  - `delete_course()` - Manager can delete courses
  - Validate teacher exists and has Teacher role
  - Validate capacity > 0
  - Validate price >= 0
  - Validate day is valid (e.g., Monday-Sunday)
  - **Note:** Price is for display only, no payment processing
- **Error Handling:**
  - Invalid teacher
  - Invalid capacity/price/day
  - Duplicate course name (optional warning)
  - Cannot delete course with active enrollments (optional safety check)

#### 2.4 Enrollment Service
- **Task:** Implement enrollment and queue logic
- **Features:**
  - `register_for_course(student_id, course_id)` - Parent enrolls child or Student enrolls self
    - Check course capacity
    - If space available → enroll immediately + create success notification
    - If full → add to waitlist at next position + create waitlist notification
    - Return enrollment status and queue position if applicable
  - `drop_course(student_id, course_id)`
    - Remove from enrollment
    - Trigger queue advancement
  - Prevent duplicate enrollments
- **Error Handling:**
  - Student doesn't exist
  - Course doesn't exist
  - Already enrolled
  - Already in waitlist

#### 2.5 Queue Advancement Service
- **Task:** Implement automatic queue advancement with in-app notifications
- **Trigger:** When a student drops or a spot opens
- **Logic:**
  1. Check if waitlist has students
  2. Get student with position = 1
  3. Enroll student automatically
  4. Create in-app notification for student/parent: "You've been enrolled in [Course Name]"
  5. Update remaining waitlist positions (decrement all by 1)
  6. Log the advancement
- **Notification:** In-app notification system (notifications displayed on dashboard)

#### 2.6 Grade Management Service
- **Task:** Implement grade CRUD for teachers
- **Features:**
  - `create_grade(student_id, course_id, grade, comments)` - Teacher only
  - `update_grade(grade_id, grade, comments)` - Teacher can update grades
  - `get_grades_by_course(course_id)` - Teacher views all student grades for their course
  - `get_grade(student_id, course_id)` - Get specific grade
  - Validate teacher is the course instructor
  - Validate student is enrolled in course
- **Error Handling:**
  - Teacher not assigned to course
  - Student not enrolled
  - Invalid grade format
  - Unauthorized access

#### 2.7 Manager Suggestion Service
- **Task:** Implement queue monitoring and suggestions
- **Features:**
  - `check_high_demand_courses()`
    - Query courses with waitlist >= 5 students
    - Return list of course_id, course_name, waitlist_count
  - Display suggestions to Manager: "Consider opening new class for [Course Name] - [X] students waiting"

#### 2.8 Notification Service
- **Task:** Implement in-app notification system
- **Features:**
  - `create_notification(user_id, message, type)`
  - `get_unread_notifications(user_id)` - Display on dashboard
  - `mark_as_read(notification_id)`
  - Auto-create notifications for:
    - Queue advancement (student enrolled from waitlist)
    - Successful enrollment
    - Waitlist addition

---

### Phase 3: Frontend Layer (Web UI)

#### 3.1 Manager Dashboard
- **Route:** `/manager/dashboard`
- **Features:**
  - Navigation menu: Users | Courses | Queue Monitor
  - Summary cards: Total Users, Total Courses, Active Enrollments

**3.1.1 User Management Page**
- **Route:** `/manager/users`
- **Components:**
  - User list table (username, role, email, created_at, actions)
  - "Create User" button → form modal/page
  - Create User Form:
    - Role dropdown (Manager/Parent/Teacher/Student/Worker)
    - Username (text)
    - Password (password field)
    - Email (text)
    - **Note:** Worker role can be created but has no dashboard/functionality in this ticket
  - Success/error messages
- **Actions:** View, Edit, Delete (Manager can edit and delete users)

**3.1.2 Course Management Page**
- **Route:** `/manager/courses`
- **Components:**
  - Course list table (name, teacher, day, capacity, enrolled, price, actions)
  - "Create Course" button → form
  - Create Course Form:
    - Course name (text)
    - Teacher dropdown (list of users with Teacher role)
    - Day dropdown (Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday)
    - Capacity (number)
    - Price (number) - display only, no payment processing
  - Edit Course Form: Manager can update all fields including capacity and day
  - Success/error messages
- **Actions:** View Details, Edit, Delete (Manager can edit and delete courses)

**3.1.3 Queue Monitor Page**
- **Route:** `/manager/queue-monitor`
- **Components:**
  - List of all courses with waitlists
  - For each course: Name, Current Enrollment, Capacity, Waitlist Count
  - Expandable waitlist (show students in order with positions)
  - Suggestions section: Highlight courses with ≥5 waiting
  - Suggestion alerts: "Consider opening new class for [Course]"

#### 3.2 Parent Dashboard
- **Route:** `/parent/dashboard`
- **Features:**
  - **Notification banner:** Display unread in-app notifications
  - View and manage children
  - Course enrollment section

**3.2.1 Manage Children Page**
- **Route:** `/parent/children`
- **Components:**
  - List of linked children (table: student name, username, enrolled courses count)
  - "Link Child" button → form/modal
  - Link Child Form:
    - Student username or ID selector (dropdown of students not yet linked)
    - Confirm button
  - "Unlink" action per child
  - Success/error messages
- **Note:** Parents link children to their own account (not Manager)

**3.2.2 Enroll Child Page**
- **Route:** `/parent/enroll`
- **Components:**
  - Child selector dropdown (if multiple children)
  - Available courses table (name, teacher, day, capacity, enrolled, price, status)
  - "Enroll" button per course
  - Status indicators: "Open", "Full - Join Waitlist"
  - Success message: "Enrolled successfully" or "Added to waitlist at position X"
  - In-app notification created on enrollment

**3.2.3 View Queue Status Page**
- **Route:** `/parent/queue-status`
- **Components:**
  - Child selector (if multiple children)
  - Child's enrollments table (course name, teacher, day, grade if available)
  - Child's waitlist table: Course Name, Position, Joined Date
  - Notifications section: Display recent notifications (queue advancement, enrollments)

#### 3.3 Teacher Dashboard
- **Route:** `/teacher/dashboard`
- **Features:**
  - View assigned courses
  - View enrolled students per course
  - **Grade management:** Teachers can create and update grades for their students

**3.3.1 My Courses Page**
- **Route:** `/teacher/courses`
- **Components:**
  - List of assigned courses
  - For each course: Name, Day, Enrolled Students Count, Capacity
  - "View Details" button per course

**3.3.2 Course Details & Grading Page**
- **Route:** `/teacher/course/<course_id>`
- **Components:**
  - Course info header (name, day, capacity, enrolled count)
  - Student roster table: Student Name, Username, Grade, Actions
  - **Grade actions:**
    - "Add Grade" button (if no grade exists) → form/modal
    - "Edit Grade" button (if grade exists) → form/modal
  - Grade Form:
    - Student (pre-selected or dropdown)
    - Grade (text/number field: e.g., "A", "B+", or 85.5)
    - Comments (optional text area)
    - Submit button
  - Success/error messages
- **Validation:**
  - Only course instructor can grade
  - Student must be enrolled
  - One grade per student per course

#### 3.4 Student Dashboard
- **Route:** `/student/dashboard`
- **Features:**
  - **Notification banner:** Display unread in-app notifications (e.g., queue advancement, enrollment)
  - View enrolled courses
  - View schedule with day
  - View grades

**3.4.1 My Schedule Page**
- **Route:** `/student/schedule`
- **Components:**
  - Table of enrolled courses: Course Name, Teacher, Day, Enrolled Date
  - Waitlist section: Courses in queue with position

**3.4.2 My Grades Page**
- **Route:** `/student/grades`
- **Components:**
  - Table: Course Name, Teacher, Day, Grade, Comments (if any)
  - Display "Not graded yet" if no grade exists

---

## Acceptance Criteria Verification

### 1. All CRUD flows work from UI ✓
- [ ] Manager can create, edit, and delete users (all roles) via web forms
- [ ] Manager can create, edit, and delete courses via web forms
- [ ] Manager can view users and courses in tables
- [ ] Parent can link/unlink children to their account
- [ ] Parent can enroll child via web form
- [ ] Parent can view enrollments and queue status
- [ ] Teacher can view courses and enrolled students
- [ ] Teacher can create and update grades for students
- [ ] Student can view schedule (with day field) and grades

### 2. Queue advancement and notifications function ✓
- [ ] Student auto-enrolls when space opens
- [ ] Waitlist positions update correctly
- [ ] Queue position visible to parents
- [ ] In-app notifications created for enrollment events and queue advancement
- [ ] Notifications displayed on Parent and Student dashboards
- [ ] Manager sees suggestions for courses with ≥5 waiting

### 3. Frontend is responsive and role-specific ✓
- [ ] Each role sees only their menu options
- [ ] Dashboards render correctly with role-specific features
- [ ] Forms are usable and validated
- [ ] Tables display correct data including day field for courses
- [ ] Price displayed but no payment processing
- [ ] Worker role can be created but has no dashboard/functionality

---

## File Structure (Suggested)

```
project/
├── data_layer/
│   ├── models.py              # User, Course, Enrollment, Waitlist, Grade, Notification models
│   ├── database.py            # DB connection, session management
│   └── crud.py                # CRUD operations for all models
├── business_logic/
│   ├── user_service.py        # User management logic (create, update, delete)
│   ├── parent_service.py      # Parent-child relationship management
│   ├── course_service.py      # Course management logic (create, update, delete, with day field)
│   ├── enrollment_service.py  # Enrollment & queue logic
│   ├── grade_service.py       # Grade CRUD for teachers
│   ├── notification_service.py # In-app notification system
│   └── manager_service.py     # Manager suggestions (high-demand courses)
├── frontend/
│   ├── app.py                 # Flask/FastAPI app entry point
│   ├── routes/
│   │   ├── auth.py            # Login/logout
│   │   ├── manager_routes.py  # Manager endpoints (users, courses, queue monitor)
│   │   ├── parent_routes.py   # Parent endpoints (children, enroll, queue status)
│   │   ├── teacher_routes.py  # Teacher endpoints (courses, grading)
│   │   └── student_routes.py  # Student endpoints (schedule, grades)
│   ├── templates/             # HTML templates
│   │   ├── base.html          # Base template with notification banner
│   │   ├── login.html
│   │   ├── manager/
│   │   │   ├── dashboard.html
│   │   │   ├── users.html     # User CRUD with edit/delete
│   │   │   ├── courses.html   # Course CRUD with edit/delete, day field
│   │   │   └── queue_monitor.html
│   │   ├── parent/
│   │   │   ├── dashboard.html # With notification banner
│   │   │   ├── children.html  # Manage parent-child links
│   │   │   ├── enroll.html    # Enroll child with day field display
│   │   │   └── queue_status.html # With notifications
│   │   ├── teacher/
│   │   │   ├── dashboard.html
│   │   │   ├── courses.html   # My courses with day field
│   │   │   └── course_detail.html # Student roster with grade CRUD
│   │   └── student/
│   │       ├── dashboard.html # With notification banner
│   │       ├── schedule.html  # With day field
│   │       └── grades.html    # View grades with comments
│   └── static/                # CSS, JS, images
├── config.py                  # Configuration (DB credentials, etc.)
└── README.md                  # Setup and run instructions
```

---

## Requirements Summary (Clarified)

### ✓ Grading System
- **Teachers CAN create and update grades** for students in their courses
- Grade model with student, course, grade value, and optional comments
- One grade per student per course

### ✓ Parent-Child Relationship
- **Parents link children to their own account** (not Manager)
- One parent can have **multiple children**
- Parent-student relationship table for many-to-many relationship
- Parents manage (link/unlink) children via their dashboard

### ✓ Course Schedule
- Courses **include a day field** (e.g., Monday, Tuesday, etc.)
- Day displayed in schedules, course lists, and enrollment pages
- No time/duration fields required for this ticket

### ✓ Notifications
- **In-app notifications only** (no email)
- Notifications displayed on Parent and Student dashboards
- Auto-created for: enrollment success, waitlist addition, queue advancement
- Simple notification table with read/unread status

### ✓ Payment
- **Display price only**, no payment processing
- Price shown in course listings and enrollment pages

### ✓ User & Course Management
- **Manager can edit and delete** both users and courses
- Full CRUD operations for Manager role
- Course capacity can be updated

### ✓ Worker Role
- **Worker role can be created** by Manager
- **No functionality or dashboard** in this ticket (future scope)

### ✓ Other Clarifications
- Students can enroll in multiple courses
- No additional authentication features required
- Queue auto-advances when spots open

---

## Estimated Effort (by phase)

- **Phase 1 (Data Layer):** ~10-14 hours
  - User & parent-child relationship: 2-3 hours
  - Course with day field: 2-3 hours
  - Enrollment & waitlist: 3-4 hours
  - Grade schema: 2-3 hours
  - Notification schema: 1-2 hours

- **Phase 2 (Business Logic):** ~14-18 hours
  - User management (CRUD): 3-4 hours
  - Parent-child service: 2-3 hours
  - Course management (CRUD with day): 3-4 hours
  - Enrollment & queue advancement: 4-5 hours
  - Grade service: 2-3 hours
  - Notification service: 2-3 hours
  - Manager suggestions: 1-2 hours

- **Phase 3 (Frontend):** ~24-36 hours (largest effort)
  - Manager dashboard (users, courses, queue monitor): 8-12 hours
  - Parent dashboard (children, enroll, queue status, notifications): 8-12 hours
  - Teacher dashboard (courses, grading): 4-6 hours
  - Student dashboard (schedule, grades, notifications): 4-6 hours

**Total Estimate:** ~48-68 hours for complete implementation

---

## Success Metrics

- All acceptance criteria from Ticket-02 are met
- Code is clean, follows OOP principles from Ticket-01
- Web UI is functional, user-friendly, and role-specific
- Automated queue system works reliably with in-app notifications
- Parent-child relationship management works seamlessly
- Grade CRUD functionality works for teachers
- Manager receives actionable suggestions for high-demand courses
- In-app notification system displays correctly
- Course day field displayed throughout the system
- Manager can successfully edit and delete users and courses
- Error handling is robust with user-friendly messages
- Price displayed correctly without payment processing
- Documentation is clear and complete

---

## Next Steps

1. **Review this plan** and ensure alignment with project goals
2. **Set up development environment** (ensure Ticket-01 is complete and functional)
3. **Begin Phase 1** (Data Layer):
   - Create parent-child relationship table
   - Add day field to Course model
   - Create Grade model
   - Create Notification model
4. **Proceed to Phase 2** (Business Logic):
   - Implement all service layers with proper validations
   - Focus on queue advancement and notification creation
5. **Build Phase 3** (Frontend):
   - Start with Manager dashboard for full CRUD
   - Then Parent dashboard with child management
   - Teacher dashboard with grading
   - Student dashboard with notifications
6. **Test thoroughly** as you build each component
7. **Update documentation** and README with setup instructions

## Implementation Tips

- **Start with data models** and test CRUD operations before building business logic
- **Build and test queue advancement** early - it's a critical feature
- **Implement notifications** alongside enrollment/queue features
- **Test role-based permissions** at each step
- **Keep UI simple and functional** - focus on usability over aesthetics
- **Use transactions** for queue advancement to ensure data consistency
- **Log important events** (enrollments, queue changes, grade updates)
