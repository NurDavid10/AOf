 ---
  TICKET 4 IMPLEMENTATION PLAN

  Phase 1: Create Teacher Routes & Dashboard Integration

  1.1 Create Teacher Routes File (app/routers/teacher_routes.py)
  - Create new router with /teacher prefix
  - Add require_teacher() helper function for role verification
  - Implement teacher-specific routes

  1.2 Implement Teacher Dashboard Route
  - Move teacher dashboard from main.py to teacher_routes.py
  - Query teacher's courses using
  CourseService.get_courses_by_teacher()
  - Calculate statistics:
    - Count of teacher's courses
    - Total enrolled students across all courses
    - Count of pending task submissions (using Task/TaskSubmission
  models)
  - Pass real data to template instead of hardcoded zeros

  1.3 Implement "View My Courses" Route (/teacher/courses)
  - Query all courses where teacher_id = current_user.id
  - Display course list with:
    - Course name, code, capacity
    - Number of enrolled students
    - Links to view students per course
    - Start/end dates
  - Create template: app/templates/teacher/courses.html

  1.4 Implement "View Students" Route
  (/teacher/courses/{course_id}/students)
  - Validate that course belongs to current teacher
  - Query CourseEnrollment filtered by course_id and status=ACTIVE
  - Display student list with:
    - Student name
    - Enrollment date
    - Current grades (if available)
    - Link to view individual student details
  - Create template: app/templates/teacher/course_students.html

  1.5 Implement "Create Task" Routes (/teacher/tasks/create GET &
  POST)
  - Display form listing teacher's courses
  - Allow teacher to:
    - Select course
    - Enter task title, description
    - Set task type (assignment, exam, project, homework)
    - Set due date
    - Set max points
  - Create task using Task model with created_by = current_user.id
  - Create template: app/templates/teacher/create_task.html

  1.6 Implement "Grade Submissions" Routes (/teacher/submissions and
  /teacher/submissions/{submission_id}/grade)
  - List all ungraded TaskSubmissions for teacher's courses
  - Allow filtering by course
  - Provide grade form for each submission
  - Update TaskSubmission with grade and feedback
  - Create templates:
    - app/templates/teacher/submissions.html
    - app/templates/teacher/grade_submission.html

  1.7 Update Teacher Dashboard Template
  - Modify app/templates/teacher/dashboard.html
  - Replace hardcoded "0" with dynamic template variables
  - Convert buttons to proper links/forms pointing to routes above

  1.8 Register Teacher Router
  - Add import in app/main.py: from app.routers import teacher_routes
  - Add router: app.include_router(teacher_routes.router)

  ---
  Phase 2: Create Student Routes & Dashboard Integration

  2.1 Create Student Routes File (app/routers/student_routes.py)
  - Create new router with /student prefix
  - Add require_student() helper function

  2.2 Implement Student Dashboard Route
  - Move student dashboard from main.py to student_routes.py
  - Query student's enrollments using
  CourseService.get_student_enrollments()
  - Calculate statistics:
    - Count of enrolled courses
    - Count of pending tasks
    - Average grade across all submissions
  - Pass real data to template

  2.3 Implement "My Courses" Route (/student/courses)
  - Query active enrollments for student_id = current_user.id
  - Display course list with:
    - Course name, code, teacher name
    - Schedule information (start/end dates)
    - Link to view course tasks
  - Create template: app/templates/student/courses.html

  2.4 Implement "My Tasks" Route (/student/tasks)
  - Query all Tasks for courses student is enrolled in
  - Show task status (submitted, graded, pending)
  - Display due dates and overdue warnings
  - Provide link to submit/view submission
  - Create template: app/templates/student/tasks.html

  2.5 Implement "View Grades" Route (/student/grades)
  - Query all TaskSubmissions for student_id = current_user.id
  - Display grades organized by course
  - Show:
    - Task name
    - Grade received / max points
    - Percentage
    - Teacher feedback
    - Average per course and overall
  - Create template: app/templates/student/grades.html

  2.6 Update Student Dashboard Template
  - Modify app/templates/student/dashboard.html
  - Replace hardcoded "0" with dynamic variables
  - Convert buttons to proper links

  2.7 Register Student Router
  - Add import and router registration in app/main.py

  ---
  Phase 3: Fix Parent-Student-Course Relationships

  3.1 Verify Parent-Student Linking
  - Confirm Student.parent_id field is properly set during user
  creation
  - Check UserService methods for creating student profiles
  - Add/fix method in UserService: create_student_profile(user_id, 
  parent_id, enrollment_date, grade_level, db)
  - Ensure parent_id is populated when Manager creates student

  3.2 Update Manager User Creation Form
  - Modify app/templates/manager/create_user.html
  - When role=Student is selected, show dropdown to select parent
  - Pass parent_id to user creation endpoint

  3.3 Update Manager User Creation Route
  (app/routers/manager_routes.py)
  - In POST /manager/users/create, capture parent_id from form
  - After creating User, create Student profile with parent_id
  - Validate that parent_id refers to valid Parent user

  3.4 Verify Enrollment Flow
  - Confirm EnrollmentService.enroll_student() creates
  CourseEnrollment correctly
  - Test that enrolled students appear in:
    - Teacher's course student list
    - Student's "My Courses"
    - Parent's child course view

  3.5 Update Parent Dashboard
  - Modify parent dashboard route in app/routers/parent_routes.py
  - Display aggregated information:
    - List of children
    - Each child's enrolled courses
    - Each child's queue positions
    - Recent grades/progress

  ---
  Phase 4: Fix Worker Issue Reporting & Manager Task Assignment

  4.1 Verify Worker Report Issue Flow
  - Confirm MaintenanceService.create_task() already sets:
    - reported_by_user_id = worker.id
    - assigned_to_worker_id = NULL (unassigned)
    - status = PENDING
  - This is already correct per current implementation

  4.2 Update Manager Maintenance View (/manager/maintenance)
  - Modify manager maintenance route in app/routers/manager_routes.py
  - Add logic to fetch unassigned tasks using
  MaintenanceService.get_unassigned_tasks()
  - Display unassigned tasks prominently with indicator (e.g.,
  "Unassigned" badge)
  - Ensure task list shows:
    - Title, description, priority, status
    - "Reported by" name
    - "Assigned to" name (or "Unassigned")

  4.3 Update Manager Maintenance Template
  - Modify app/templates/manager/maintenance.html
  - Add visual distinction for unassigned tasks (e.g., yellow
  highlight, "UNASSIGNED" label)
  - Add "Assign" button/form for each unassigned task

  4.4 Verify Task Assignment Flow
  - Confirm POST /manager/maintenance/{task_id}/assign route exists
  and works
  - Uses MaintenanceService.assign_task() to set assigned_to_worker_id
  - After assignment, task should appear in worker's task list

  4.5 Update Worker Dashboard & Task View
  - Confirm worker dashboard at /worker/dashboard shows only tasks
  with assigned_to_worker_id = current_worker.id
  - Confirm /worker/tasks route filters correctly
  - Test that newly assigned tasks appear for worker immediately

  4.6 Test Full Issue Reporting Flow
  - Worker submits issue via /worker/report-issue
  - Issue created with assigned_to_worker_id = NULL
  - Manager sees issue in /manager/maintenance as unassigned
  - Manager assigns to a worker
  - Worker sees task in /worker/tasks

  ---
  Phase 5: Add Error Handling & Validation

  5.1 Course-Teacher Assignment Validation
  - In CourseService.create_course() and update_course():
    - Validate teacher_id points to a user with role=TEACHER
    - Return friendly error: "Invalid teacher. Please select a valid
  teacher."

  5.2 Student Enrollment Validation
  - In EnrollmentService.enroll_student():
    - Check student exists and has role=STUDENT
    - Check course exists
    - Check course is not full (or add to queue)
    - Return friendly errors for each case

  5.3 Maintenance Task Assignment Validation
  - In MaintenanceService.assign_task():
    - Validate worker_id points to user with role=WORKER
    - Return friendly error: "Invalid worker. Please select a valid
  worker."

  5.4 Parent-Student Validation
  - When creating Student profile:
    - Validate parent_id is null or points to valid Parent
    - Return error: "Invalid parent. Please select a valid parent."

  5.5 Add Try-Except Blocks
  - Wrap all route handlers in try-except
  - Catch common exceptions:
    - HTTPException for authorization
    - ValueError for invalid inputs
    - Generic Exception for unexpected errors
  - Return user-friendly error messages via session flash messages
  - Never show raw Python tracebacks to users

  5.6 Add Permission Checks
  - Teacher viewing course students: verify course belongs to teacher
  - Teacher grading submission: verify submission is for teacher's
  course
  - Worker updating task: verify task is assigned to worker
  - Parent viewing child data: verify child belongs to parent

  ---
  Phase 6: Database Schema Verification & Fixes

  6.1 Verify Foreign Key Constraints
  - Confirm all relationships have proper FK constraints:
    - Course.teacher_id → Teacher.user_id
    - Student.parent_id → Parent.user_id
    - CourseEnrollment.student_id → Student.user_id
    - CourseEnrollment.course_id → Course.id
    - MaintenanceTask.assigned_to_worker_id → Worker.user_id
    - MaintenanceTask.reported_by_user_id → User.id

  6.2 Add Missing Indexes
  - Ensure indexes exist on frequently queried fields:
    - Course.teacher_id
    - CourseEnrollment.student_id
    - CourseEnrollment.course_id
    - MaintenanceTask.assigned_to_worker_id
    - TaskSubmission.student_id

  6.3 Test Cascade Behaviors
  - Test deletion cascades work correctly:
    - Deleting course deletes enrollments
    - Deleting user sets teacher_id to NULL in courses
    - Deleting parent sets student.parent_id to NULL

  ---
  Phase 7: Testing & Verification

  7.1 Test Teacher Flow
  - Create Manager, Teacher, and Course
  - Assign teacher to course as Manager
  - Login as Teacher
  - Verify "My Courses" shows the assigned course
  - Verify "View Students" shows enrolled students
  - Create a task for the course
  - Grade a submission

  7.2 Test Student Flow
  - Create Student with parent linkage
  - Enroll student in course (via Parent or Manager)
  - Login as Student
  - Verify "My Courses" shows enrolled course
  - Verify "My Tasks" shows course tasks
  - Submit a task
  - View grades after teacher grades submission

  7.3 Test Parent Flow
  - Create Parent and link Student(s)
  - Login as Parent
  - Verify children list shows linked students
  - Enroll child in course
  - Verify child's enrollments and queue positions display
  - View child's grades

  7.4 Test Worker Issue Flow
  - Login as Worker
  - Submit issue via "Report Issue"
  - Verify issue does NOT appear in worker's task list (because
  unassigned)
  - Login as Manager
  - Verify issue appears as "Unassigned" in maintenance view
  - Assign issue to a worker
  - Login as Worker
  - Verify assigned task now appears in task list
  - Update task status

  7.5 Test Edge Cases
  - Course at full capacity → student added to queue
  - Drop enrollment → next student promoted from queue
  - Assigning course to non-teacher user → error
  - Assigning task to non-worker user → error
  - Teacher accessing another teacher's course → denied
  - Worker accessing unassigned task → denied

  7.6 Test Data Integrity
  - Verify dashboard counts match database records
  - Verify relationships are consistent across all views
  - Check that queue positions update correctly
  - Ensure grades display correctly across student/parent views

  ---
  Phase 8: Documentation & Final Updates

  8.1 Update README
  - Document new routes and functionality
  - Add testing instructions for all roles
  - Document the full user flow for each role

  8.2 Add Code Comments
  - Ensure all new routes have docstrings
  - Document complex business logic
  - Add inline comments for non-obvious code

  8.3 Update Project Plan Documents
  - Mark Ticket 4 tasks as completed
  - Document any deviations from original plan
  - Note any future enhancements

  ---
  Summary of Key Changes

  | Component      | Change Required
                                                                 |
  |----------------|--------------------------------------------------
  ---------------------------------------------------------------|
  | New Files      | teacher_routes.py, student_routes.py, multiple
  HTML templates                                                   |
  | Modified Files | main.py, manager_routes.py, user_service.py,
  manager/maintenance templates, teacher/student dashboard templates |
  | Database       | Verify FK constraints, add indexes (no schema
  changes needed)                                                   |
  | Services       | Add create_student_profile() with parent_id
  support, verify existing methods
  |
  | Templates      | Create 8-10 new templates, update 3-4 existing
  ones                                                             |
  | Routes         | Add ~15 new routes across teacher and student
  routers                                                           |
