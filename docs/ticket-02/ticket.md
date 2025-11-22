Ticket 2 – User, Course & Queue Management (Full Stack)

Type: Story
Depends on: Ticket 1

Goal: Implement core functionalities for Managers, Parents, Teachers, and Students.

Scope / Requirements

User Management: Manager can create users for all roles 



; login validates credentials.

Course Management: Manager creates courses (name, teacher, capacity, price).

Enrollment + Queue: Parent registers child; if course is full, child joins waiting list and system auto-updates when a slot opens 



.

Queue Monitoring: Parents view child’s queue position; Manager views course queues and receives suggestions to open new classes when ≥5 students waiting.

Frontend (Web UI):

Role-based menus and dashboards.

Manager → users & courses; Parent → enroll child / view queue; Teacher → grades; Student → schedule & grades.

All actions available through web forms and tables.

Acceptance Criteria

All CRUD flows work from UI.

Queue advancement and notifications function as described.

Front-end is responsive and role-specific.

---

## Cleanup Summary

**No significant cleanup required for this ticket.** The ticket description is concise and focused on its scope (User, Course & Queue Management). No duplicate logic or overlapping implementations found.

**Note:** Ticket 04 (Worker CLI implementation) has been removed. Worker functionality is fully defined in Tickets 01-03 via web interface only.