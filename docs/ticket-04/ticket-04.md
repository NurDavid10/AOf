Ticket 4 – Fix Role Dashboards & Entity Relationships (Courses, Enrollments, Maintenance Tasks)

Type: Bugfix / Feature Completion
Depends on: Tickets 1–3

1. Background

The core web UI and dashboards for Manager, Teacher, Student, Parent and Worker already exist and render correctly, but several flows required by the project spec are not fully wired to the database and business logic. 

פרויקט (1)

Current problems:

When a Manager creates a course and assigns a Teacher, that course does not appear in the Teacher’s “My Courses” list and related views.

Teacher Dashboard quick–action buttons (e.g. View My Courses, Create Task, Grade Submissions, View Students) either do nothing, lead to empty pages, or are not backed by working routes/queries.

Students are not properly linked to:

their Parent (parent–child relationship), and

their Courses (student–course enrollments).
As a result, Student and Parent dashboards cannot display correct schedules, grades, or enrollment/queue information as required by the project.

On the Worker Dashboard, existing assigned tasks are displayed correctly, but when a Worker uses “Report Issue”:

the new issue is not visible for the Worker, and

it is also not visible for the Manager.
We want new issues reported by Workers to appear as unassigned maintenance tasks for the Manager, who can then assign them to a specific Worker.

The goal of this ticket is to fix the data relationships and dashboard queries so that all roles see consistent, correct information across the system.

2. Goals

Ensure that Teacher, Student, Parent, and Worker dashboards are fully connected to the database and business logic.

Implement the full relationship chain:
Parent → Student(s) → Course(s) → Teacher, plus Manager ↔ Worker ↔ Tasks/Issues.

Keep the existing architecture from Tickets 1–3 (OOP model, 3-layer separation, Flask/FastAPI web app) and only complete/fix the missing flows, not redesign everything.

3. Scope & Requirements
3.1 Course–Teacher relationship

Make sure the Course entity stores a reference to the assigned Teacher (e.g. teacher_id foreign key to the users table where role = 'teacher').

When the Manager creates or edits a course in the Manager UI:

Persist the teacher_id correctly in the DB.

In the Teacher dashboard:

Implement the query/service that returns all courses where teacher_id = current_teacher.id.

The “My Courses” count and the “View My Courses” page must use this data.

If no courses are assigned, the UI may show 0 with an empty state message, but as soon as the Manager assigns a course, it must appear for that Teacher.

3.2 Parent–Student–Course relationships (enrollment)

Implement or fix the data model so that:

A Parent is linked to one or more Students

Either via students.parent_id or a separate parent_students mapping table.

A Student is linked to one or more Courses through an Enrollment/registrations table, e.g.:
enrollments(id, student_id, course_id, status, queue_position, ...).

Update the Parent flows:

When a Parent registers a child to a course (including waitlist logic from Ticket 2), create/update the correct enrollment record.

Update the Teacher flows:

On “View Students” for a course, show all students with enrollments.course_id = this_course.id and appropriate status.

Update the Student dashboard:

“View Schedule” should be based on the Student’s enrollments and the course schedule fields.

“View Grades” should show grades per course for the current Student using the existing grade model/logic.

Respect the queue/waitlist behavior from the project spec (child goes to waitlist when course is full, system auto-advances when a slot opens). 

פרויקט (1)

3.3 Teacher actions & dashboard routing

Implement or fix backend routes/services + templates for all Teacher dashboard quick actions:

View My Courses – list of teacher’s courses with basic info and links to view enrolled students.

Create Task – page or form allowing the Teacher to create academic tasks/assignments for a course (if this feature already exists, just connect the button).

Grade Submissions – list of pending submissions (or at least a placeholder connected to the correct route querying related data).

View Students – list students per course (based on enrollments, see 3.2).

Ensure all these actions go through the business logic layer, not directly from controller to DB.

3.4 Worker maintenance issues & Manager tasks

Adjust the “Report Issue” flow on the Worker dashboard:

When a Worker submits a new issue, create a maintenance task record in the DB with:

created_by_worker_id = current_worker.id

assigned_worker_id = NULL (unassigned)

status = 'pending' (or equivalent)

priority, title, description, created_at, etc.

In the Manager dashboard:

Add/update a view under “Manage Employee Tasks” (or equivalent) to show:

All tasks, including newly reported issues with assigned_worker_id IS NULL clearly marked as unassigned.

Allow the Manager to assign an unassigned task to a Worker (update assigned_worker_id).

In the Worker dashboard:

“View All Tasks” must show all tasks where assigned_worker_id = current_worker.id.

Once the Manager assigns a previously reported issue to that Worker, it should appear in the Worker’s task list.

Keep using the existing MaintenanceService / worker_routes.py / equivalent services mentioned in Ticket 3, just complete the missing parts. 

ticket

3.5 Error handling & validation

Add proper validation and try/except handling around:

Assigning a course to a non-teacher user.

Enrolling a student to a course that does not exist or is full.

Assigning a maintenance task to a non-worker user.

Show friendly error messages in the web UI instead of raw tracebacks.

4. Out of Scope

No major visual redesign of the dashboards (keep existing layout/styles).

No changes to the authentication system or role creation logic, except where needed to link IDs correctly.

No removal of existing business logic unless it is clearly wrong or duplicated.

5. Acceptance Criteria

Teacher Courses

Create a Teacher user and a course assigned to that Teacher as Manager.

Log in as that Teacher → “My Courses” shows the created course, and “View My Courses” lists it.

Parent → Student → Course

Create Parent and Student users; link Student to Parent.

As Parent, register the Student to a course:

The course now shows the student in its enrolled list (or waitlist, depending on capacity).

Student dashboard shows the course in “View Schedule”.

If grades are entered for that student, they appear in “View Grades”.

Teacher Dashboard Buttons

All four quick-action buttons navigate to real pages backed by working queries/services (no 404 / dead buttons).

“View Students” for a course shows the correct enrolled students.

Worker Issues & Manager Tasks

As Worker, use “Report Issue” to submit a new problem.

As Manager, see the new issue in the maintenance/task management view as an unassigned task.

Assign the task to a Worker.

As that Worker, see the task appear in “View All Tasks” and be able to update its status.

Data Integrity

DB constraints/joins support:

Course.teacher_id → Teacher

Student ↔ Parent

Student ↔ Course (enrollments)

Task.created_by_worker_id and Task.assigned_worker_id (optional FK).

All dashboards show consistent numbers (e.g., Teacher’s “My Courses” count matches the DB).