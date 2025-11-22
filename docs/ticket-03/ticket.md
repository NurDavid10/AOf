Ticket 3 – Financial & Maintenance Modules + Reports (Web UI Integration)

Type: Story
Depends on: Tickets 1 & 2

Goal: Complete the remaining system modules for finance tracking and facility maintenance, and build summary dashboards.

Scope / Requirements

Financial Tracking: Parents record payments per course; Managers view income / expense reports and net results 



.

Maintenance Tasks: Managers assign tasks to workers; workers update status (pending / in progress / done); teachers and workers can report new issues 



.

Reports & Dashboards:

Manager dashboard: students per course, queues, open tasks, budget summary.

Parent dashboard: child progress and payments.

Worker dashboard: assigned tasks.

Frontend: All financial and maintenance features available via web pages with tables and forms; no CLI required.

Acceptance Criteria

Data persists and updates through DB layer.

Reports summarize data accurately.

System meets all OOP + 3-layer + web UI requirements from the original brief 

---

## Cleanup Summary

**No significant cleanup required for this ticket.** The ticket description is concise and focused on its scope (Financial & Maintenance Modules). Worker functionality is properly described via web interface only (no CLI required).

**Note:** Ticket 04 (Worker CLI implementation) has been removed. Worker functionality is fully defined in Tickets 01-03 via web interface through `app/routers/worker_routes.py` and `MaintenanceService`.

