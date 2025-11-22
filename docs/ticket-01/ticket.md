Ticket 1 – Core System Architecture (OOP + DB + Frontend Foundation)

Type: Epic
Goal: Build the 3-layer architecture and domain model for “Academic Tomorrow” Learning Center Management System.

Scope / Requirements

Implement full OOP: inheritance (base User → Manager / Parent / Teacher / Student / Worker), polymorphism (overridden methods), encapsulation (getters/setters).

Create the three layers:
1️⃣ Data Layer – database schema + CRUD for users, courses, tasks, payments, queues.
2️⃣ Business Logic – validations (e.g., unique username), automated queue handling, financial calculations.
3️⃣ Frontend Layer (MANDATORY) – Flask or FastAPI web app with login and role-based routing. All roles access the system via web interface only.

Provide DB initialization with dummy data and re-runnable schema creation scripts.

Add error handling (try/except) and user-friendly messages.

Document all classes and methods + English README explaining run steps.

Acceptance Criteria

Code runs and connects frontend ↔ business logic ↔ DB.

Login page distinguishes roles correctly.

README + technical guide covers local DB configuration (host, user, password, DB name) as required 

---

## Cleanup Summary

**No significant cleanup required for this ticket.** The ticket description is concise and focused on its scope (Core System Architecture). This is the foundation ticket and serves as the base for all other tickets.

**Note:** Updated to clarify that all roles (including Worker) access the system via web interface only. Ticket 04 (Worker CLI implementation) has been removed as Worker functionality is fully defined in Tickets 01-03 via web interface.
