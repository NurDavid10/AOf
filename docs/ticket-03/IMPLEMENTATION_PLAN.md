# Ticket-03 Implementation Plan
## Financial & Maintenance Modules + Reports (Web UI Integration)

**Type**: Story
**Depends on**: Tickets 1 & 2 (completed)
**Estimated Duration**: 3-5 days

---

## Overview

This ticket adds the final two major modules to the system:
1. **Financial Tracking** - Income (payments) and expenses with reports
2. **Maintenance Tasks** - Task management for facility maintenance
3. **Enhanced Dashboards** - Comprehensive views for all roles

### Assumptions
- Tickets 1 & 2 are complete, meaning:
  - User management works (all 5 roles)
  - Course and enrollment system functional
  - Queue system operational
  - Basic dashboards exist for each role
  - Authentication and role-based access working

---

## Implementation Tasks Breakdown

### Task 1: Financial Tracking - Database & Models
**Duration**: 2-3 hours

#### 1.1 Create Payment Model
Location: `app/models/payment.py`

```python
class Payment(db.Model):
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_date = db.Column(db.Date, nullable=False)
    payment_method = db.Column(db.Enum('cash', 'card', 'transfer'), nullable=False)
    receipt_number = db.Column(db.String(50), unique=True)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    parent = db.relationship('User', foreign_keys=[parent_id])
    student = db.relationship('User', foreign_keys=[student_id])
    course = db.relationship('Course')
```

#### 1.2 Create Expense Model
Location: `app/models/expense.py`

```python
class Expense(db.Model):
    __tablename__ = 'expenses'

    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False)  # salary, maintenance, utilities, supplies
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    expense_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text)
    created_by_manager_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    created_by = db.relationship('User')
```

#### 1.3 Database Migration
```bash
# Create migration
alembic revision --autogenerate -m "Add payment and expense models"
alembic upgrade head
```

---

### Task 2: Financial Tracking - Service Layer
**Duration**: 2-3 hours

#### 2.1 Create PaymentService
Location: `app/services/payment_service.py`

```python
class PaymentService:
    @staticmethod
    def record_payment(parent_id, student_id, course_id, amount,
                       payment_date, payment_method, notes=None):
        """Record a payment from parent for student's course"""
        # Validate parent-student relationship
        # Validate student enrolled in course
        # Generate receipt number
        # Create payment record
        # Return payment object or raise exception

    @staticmethod
    def get_parent_payments(parent_id, start_date=None, end_date=None):
        """Get all payments made by a parent"""

    @staticmethod
    def get_course_payments(course_id):
        """Get all payments for a specific course"""

    @staticmethod
    def calculate_total_income(start_date, end_date):
        """Calculate total income in date range"""

    @staticmethod
    def get_income_by_course(start_date, end_date):
        """Get income breakdown by course"""
```

#### 2.2 Create ExpenseService
Location: `app/services/expense_service.py`

```python
class ExpenseService:
    @staticmethod
    def create_expense(category, amount, expense_date, description, manager_id):
        """Record an expense"""

    @staticmethod
    def get_expenses(start_date=None, end_date=None, category=None):
        """Get expenses with optional filters"""

    @staticmethod
    def calculate_total_expenses(start_date, end_date):
        """Calculate total expenses in date range"""

    @staticmethod
    def get_expenses_by_category(start_date, end_date):
        """Get expense breakdown by category"""
```

#### 2.3 Create FinancialReportService
Location: `app/services/financial_report_service.py`

```python
class FinancialReportService:
    @staticmethod
    def generate_financial_summary(start_date, end_date):
        """
        Returns:
        {
            'total_income': Decimal,
            'total_expenses': Decimal,
            'net_result': Decimal,
            'income_by_course': [...],
            'expenses_by_category': [...]
        }
        """

    @staticmethod
    def get_budget_summary():
        """Get current month budget summary for dashboard"""
```

---

### Task 3: Financial Tracking - Frontend (Parent)
**Duration**: 2-3 hours

#### 3.1 Record Payment Form
Location: `templates/parent/make_payment.html`

**Features:**
- Dropdown to select child (only enrolled children)
- Dropdown to select course (only child's enrolled courses)
- Amount input field
- Payment date picker
- Payment method radio buttons (Cash, Card, Transfer)
- Notes textarea
- Submit button

**Route:** `POST /parent/payment/create`

#### 3.2 Payment History View
Location: `templates/parent/payment_history.html`

**Features:**
- Table showing:
  - Receipt number
  - Date
  - Student name
  - Course name
  - Amount
  - Payment method
- Filter by date range
- Sort by date (newest first)
- Total amount paid displayed

**Route:** `GET /parent/payments`

---

### Task 4: Financial Tracking - Frontend (Manager)
**Duration**: 2-3 hours

#### 4.1 Financial Report Page
Location: `templates/manager/financial_report.html`

**Features:**
- Date range selector (start date, end date)
- Summary cards:
  - Total Income (green)
  - Total Expenses (red)
  - Net Result (blue if positive, red if negative)
- Income breakdown by course (table + chart)
- Expense breakdown by category (table + chart)
- Export button (optional: CSV/PDF)

**Route:** `GET /manager/financial-report`

#### 4.2 Record Expense Form
Location: `templates/manager/expense_create.html`

**Features:**
- Category dropdown (Salary, Maintenance, Utilities, Supplies, Other)
- Amount input
- Date picker
- Description textarea
- Submit button

**Route:** `POST /manager/expense/create`

#### 4.3 View Expenses
Location: `templates/manager/expenses_list.html`

**Features:**
- Table with all expenses
- Filter by category and date range
- Edit/delete functionality
- Total expenses displayed

**Route:** `GET /manager/expenses`

---

### Task 5: Maintenance System - Database & Models
**Duration**: 2-3 hours

#### 5.1 Create MaintenanceTask Model
Location: `app/models/maintenance_task.py`

```python
class MaintenanceTask(db.Model):
    __tablename__ = 'maintenance_tasks'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    priority = db.Column(db.Enum('low', 'medium', 'high', 'urgent'), default='medium')
    status = db.Column(db.Enum('pending', 'in_progress', 'completed', 'cancelled'),
                       default='pending')
    assigned_to_worker_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    reported_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    started_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    notes = db.Column(db.Text)

    # Relationships
    assigned_to = db.relationship('User', foreign_keys=[assigned_to_worker_id])
    reported_by = db.relationship('User', foreign_keys=[reported_by_user_id])
```

#### 5.2 Database Migration
```bash
alembic revision --autogenerate -m "Add maintenance task model"
alembic upgrade head
```

---

### Task 6: Maintenance System - Service Layer
**Duration**: 2-3 hours

#### 6.1 Create MaintenanceService
Location: `app/services/maintenance_service.py`

```python
class MaintenanceService:
    @staticmethod
    def create_task(title, description, priority, reported_by_user_id):
        """Create a new maintenance task"""

    @staticmethod
    def assign_task(task_id, worker_id, assigned_by_manager_id):
        """Assign task to a worker"""
        # Validate worker role
        # Update task status to 'pending'
        # Log assignment

    @staticmethod
    def update_task_status(task_id, new_status, updated_by_user_id):
        """Update task status"""
        # Validate status transition
        # Set timestamps (started_at, completed_at)
        # Log update

    @staticmethod
    def get_worker_tasks(worker_id, status=None):
        """Get tasks assigned to a worker"""

    @staticmethod
    def get_all_tasks(status=None, priority=None):
        """Get all tasks with optional filters"""

    @staticmethod
    def get_open_tasks_count():
        """Count tasks that are pending or in_progress"""

    @staticmethod
    def add_notes(task_id, notes, user_id):
        """Add notes to a task"""
```

---

### Task 7: Maintenance System - Frontend (Manager)
**Duration**: 2-3 hours

#### 7.1 Maintenance Tasks Dashboard
Location: `templates/manager/maintenance_tasks.html`

**Features:**
- Tabs for filtering: All, Pending, In Progress, Completed
- Task cards/table showing:
  - Title
  - Priority (color-coded badge)
  - Status (color-coded badge)
  - Assigned worker (or "Unassigned")
  - Reported by
  - Date created
- Actions:
  - Assign to worker (modal with worker dropdown)
  - View details
  - Mark as cancelled
- Create new task button
- Filter by priority

**Route:** `GET /manager/maintenance`

#### 7.2 Create Maintenance Task Form
Location: `templates/manager/maintenance_create.html`

**Features:**
- Title input
- Description textarea
- Priority dropdown
- Optional: Assign to worker immediately
- Submit button

**Route:** `POST /manager/maintenance/create`

#### 7.3 Assign Task Modal/Page
**Features:**
- Select worker from dropdown (only workers)
- Confirm assignment
- Auto-notification to worker

**Route:** `POST /manager/maintenance/<task_id>/assign`

---

### Task 8: Maintenance System - Frontend (Worker)
**Duration**: 2-3 hours

#### 8.1 Worker Dashboard - Tasks View
Location: `templates/worker/tasks.html`

**Features:**
- Tabs: Pending, In Progress, Completed
- Task cards showing:
  - Title
  - Description
  - Priority
  - Status
  - Date assigned
- Actions per task:
  - Start Task (pending → in_progress)
  - Complete Task (in_progress → completed)
  - Add notes
- Statistics: Total assigned, In progress, Completed

**Route:** `GET /worker/tasks`

#### 8.2 Task Detail View
Location: `templates/worker/task_detail.html`

**Features:**
- Full task information
- Status update buttons
- Notes/comments section
- Activity log

**Route:** `GET /worker/task/<task_id>`

---

### Task 9: Maintenance System - Frontend (Teacher & Worker)
**Duration**: 1-2 hours

#### 9.1 Report Issue Form
Location: `templates/teacher/report_issue.html` and `templates/worker/report_issue.html`

**Features:**
- Title input
- Description textarea
- Priority dropdown
- Submit button
- Success message: "Issue reported. A manager will review it."

**Routes:**
- `GET /teacher/report-issue`
- `POST /teacher/report-issue`
- `GET /worker/report-issue`
- `POST /worker/report-issue`

---

### Task 10: Enhanced Dashboards
**Duration**: 3-4 hours

#### 10.1 Manager Dashboard Enhancement
Location: `templates/manager/dashboard.html`

**Add/Update these sections:**

1. **Statistics Cards Row:**
   - Total Users
   - Total Courses
   - Students Waiting in Queues
   - Open Maintenance Tasks
   - This Month's Net Income

2. **Students per Course Chart:**
   - Bar chart showing enrollment count per course
   - Highlight courses at/near capacity

3. **Queue Summary Table:**
   - Course name
   - Students enrolled / Capacity
   - Students waiting
   - Action: "View Queue" button

4. **Budget Summary (Current Month):**
   - Income: $X
   - Expenses: $Y
   - Net: $Z
   - Link to detailed financial report

5. **Open Maintenance Tasks:**
   - Count by status
   - List of urgent/high priority tasks
   - Link to full maintenance dashboard

6. **Quick Actions:**
   - Create User
   - Create Course
   - Create Expense
   - Create Maintenance Task

**Route:** `GET /manager/dashboard`

#### 10.2 Parent Dashboard Enhancement
Location: `templates/parent/dashboard.html`

**Add/Update these sections:**

1. **Children Overview Cards:**
   - For each child:
     - Name
     - Enrolled courses count
     - Queue positions (if any)
     - Recent grades

2. **Courses & Enrollment Status:**
   - Table per child:
     - Course name
     - Status (Enrolled / Waiting - position X)
     - Teacher name
     - Latest grade

3. **Payment Summary:**
   - Total paid this month
   - Total paid all time
   - Recent payments (last 5)
   - Button: "Make Payment" | "View History"

4. **Queue Status:**
   - Only if child has queue positions
   - Course name + position
   - Estimated wait info

**Route:** `GET /parent/dashboard`

#### 10.3 Worker Dashboard Enhancement
Location: `templates/worker/dashboard.html`

**Add/Update these sections:**

1. **Task Statistics:**
   - Total assigned
   - Pending
   - In Progress
   - Completed (all time)

2. **Tasks by Status:**
   - Tabs or sections for each status
   - Show top 5-10 tasks per status

3. **Urgent Tasks Alert:**
   - Highlight urgent/high priority tasks
   - Show overdue tasks (if date tracking added)

4. **Quick Actions:**
   - Report New Issue

**Route:** `GET /worker/dashboard`

#### 10.4 Teacher Dashboard (Minor Updates)
Location: `templates/teacher/dashboard.html`

**Keep existing + add:**
- Quick link to report maintenance issue
- Course statistics (students per course, average grades)

#### 10.5 Student Dashboard (Minor Updates)
Location: `templates/student/dashboard.html`

**Keep existing + add:**
- Visual schedule/calendar view (optional enhancement)
- Grade trends chart (optional)

---

### Task 11: Chart Visualizations
**Duration**: 2-3 hours

#### 11.1 Add Chart.js Library
In `templates/base.html`:
```html
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0"></script>
```

#### 11.2 Implement Charts

**Manager Dashboard Charts:**
1. **Students per Course** (Bar Chart)
   - X-axis: Course names
   - Y-axis: Student count
   - Show capacity as reference line

2. **Financial Overview** (Pie Chart)
   - Income by course

3. **Expense Breakdown** (Pie Chart)
   - Expenses by category

**Financial Report Charts:**
1. **Income vs Expenses** (Bar Chart - side by side)
2. **Income by Course** (Horizontal Bar Chart)
3. **Expenses by Category** (Doughnut Chart)

**Implementation:**
- Create JavaScript functions in `static/js/charts.js`
- Pass data from Flask template context
- Render charts on page load

---

### Task 12: Navigation & UI Polish
**Duration**: 1-2 hours

#### 12.1 Update Navigation Menus

**Manager Menu Items:**
- Dashboard
- Users
- Courses
- Queues
- **Financial** (new dropdown):
  - Financial Report
  - Record Expense
  - View Expenses
- **Maintenance** (new):
  - View Tasks
  - Create Task
- Logout

**Parent Menu Items:**
- Dashboard
- My Children
- Enroll Child
- Queue Status
- **Payments** (new dropdown):
  - Make Payment
  - Payment History
- Logout

**Worker Menu Items:**
- Dashboard
- **My Tasks** (new)
- **Report Issue** (new)
- Logout

**Teacher Menu Items:**
- Dashboard
- My Courses
- Assign Grades
- **Report Issue** (new)
- Logout

#### 12.2 UI Improvements
- Consistent button styles
- Success/error flash messages styling
- Form validation styling
- Responsive tables (Bootstrap table-responsive)
- Loading indicators for form submissions
- Confirmation modals for important actions

---

### Task 13: Testing & Validation
**Duration**: 2-3 hours

#### 13.1 Functional Testing Checklist

**Financial Module:**
- [ ] Parent can record payment for enrolled child
- [ ] Parent cannot record payment for non-enrolled course
- [ ] Payment appears in parent's payment history
- [ ] Payment appears in manager's financial report
- [ ] Manager can record expenses
- [ ] Financial report calculates totals correctly
- [ ] Income by course breakdown is accurate
- [ ] Expense by category breakdown is accurate
- [ ] Net result calculation is correct (income - expenses)
- [ ] Date range filtering works

**Maintenance Module:**
- [ ] Manager can create maintenance task
- [ ] Manager can assign task to worker
- [ ] Worker sees assigned task in their dashboard
- [ ] Worker can update task status (pending → in_progress → completed)
- [ ] Teacher can report maintenance issue
- [ ] Worker can report maintenance issue
- [ ] Reported issues appear in manager's maintenance dashboard
- [ ] Open tasks count is accurate
- [ ] Priority filtering works
- [ ] Status filtering works

**Dashboards:**
- [ ] Manager dashboard shows all required metrics
- [ ] Students per course chart renders correctly
- [ ] Budget summary shows current month data
- [ ] Queue summary shows all courses with waiting students
- [ ] Open tasks count is accurate
- [ ] Parent dashboard shows all children
- [ ] Payment summary shows correct totals
- [ ] Worker dashboard shows task statistics
- [ ] All dashboards load without errors

**Integration:**
- [ ] Data persists across sessions
- [ ] All role permissions enforced correctly
- [ ] Navigation menus show correct items per role
- [ ] No unauthorized access to other roles' pages
- [ ] Forms validate inputs properly
- [ ] Error messages are user-friendly

#### 13.2 Edge Cases Testing
- [ ] Parent with multiple children can pay for each
- [ ] Worker with no assigned tasks sees empty state
- [ ] Financial report with no data shows zeros
- [ ] Task reassignment from one worker to another
- [ ] Payment with invalid amount rejected
- [ ] Task status updates in correct order only
- [ ] Date range selection with invalid dates handled

#### 13.3 UI/UX Testing
- [ ] All pages responsive on mobile
- [ ] Charts render properly
- [ ] Tables paginate if many records
- [ ] Forms have clear labels
- [ ] Success messages display properly
- [ ] Error messages are helpful
- [ ] Loading states for long operations
- [ ] All links work correctly

---

### Task 14: Documentation
**Duration**: 2-3 hours

#### 14.1 Update README.md
Add sections:
- **Financial Module** - How to record payments and expenses
- **Maintenance Module** - How to create and manage tasks
- **Dashboard Features** - Overview of each role's dashboard

#### 14.2 Create User Guide
Location: `docs/ticket-03/USER_GUIDE.md`

**Sections:**
1. **For Parents:**
   - How to make a payment
   - How to view payment history

2. **For Managers:**
   - How to record expenses
   - How to view financial reports
   - How to create maintenance tasks
   - How to assign tasks to workers

3. **For Workers:**
   - How to view assigned tasks
   - How to update task status
   - How to report new issues

4. **For Teachers:**
   - How to report maintenance issues

#### 14.3 Update Technical Documentation
Location: `docs/TECHNICAL_GUIDE.md`

Add sections:
- Financial module architecture
- Maintenance module architecture
- Service layer documentation for new services
- Database schema updates
- API endpoints (if applicable)

#### 14.4 Code Documentation
- [ ] Add docstrings to all new classes
- [ ] Add docstrings to all new methods
- [ ] Add inline comments for complex logic
- [ ] Type hints for function parameters

---

## Database Initialization Updates

Update `scripts/init_db.py` to include dummy data for:

### Payments
```python
# Sample payments
payments = [
    Payment(parent_id=1, student_id=3, course_id=1,
            amount=150.00, payment_date=date(2024, 1, 15),
            payment_method='card', receipt_number='RCP001'),
    # ... more payments
]
```

### Expenses
```python
# Sample expenses
expenses = [
    Expense(category='salary', amount=2000.00,
            expense_date=date(2024, 1, 30),
            description='Teacher salary - January',
            created_by_manager_id=1),
    # ... more expenses
]
```

### Maintenance Tasks
```python
# Sample tasks
tasks = [
    MaintenanceTask(title='Fix broken chair in Room 101',
                    description='Chair leg is broken',
                    priority='medium', status='pending',
                    reported_by_user_id=2),  # Teacher
    MaintenanceTask(title='AC not working in Room 203',
                    description='Air conditioning unit not cooling',
                    priority='high', status='in_progress',
                    assigned_to_worker_id=5,  # Worker
                    reported_by_user_id=1),  # Manager
    # ... more tasks
]
```

---

## File Structure for Ticket-03

```
app/
├── models/
│   ├── payment.py              # NEW
│   ├── expense.py              # NEW
│   └── maintenance_task.py     # NEW
├── services/
│   ├── payment_service.py      # NEW
│   ├── expense_service.py      # NEW
│   ├── financial_report_service.py  # NEW
│   └── maintenance_service.py  # NEW
├── routes/
│   ├── manager.py              # UPDATE - add financial & maintenance routes
│   ├── parent.py               # UPDATE - add payment routes
│   ├── teacher.py              # UPDATE - add report issue route
│   └── worker.py               # UPDATE - add task management routes
├── templates/
│   ├── manager/
│   │   ├── dashboard.html      # UPDATE
│   │   ├── financial_report.html       # NEW
│   │   ├── expense_create.html         # NEW
│   │   ├── expenses_list.html          # NEW
│   │   ├── maintenance_tasks.html      # NEW
│   │   └── maintenance_create.html     # NEW
│   ├── parent/
│   │   ├── dashboard.html      # UPDATE
│   │   ├── make_payment.html   # NEW
│   │   └── payment_history.html # NEW
│   ├── teacher/
│   │   ├── dashboard.html      # UPDATE
│   │   └── report_issue.html   # NEW
│   └── worker/
│       ├── dashboard.html      # UPDATE (create if not exists)
│       ├── tasks.html          # NEW
│       ├── task_detail.html    # NEW
│       └── report_issue.html   # NEW
└── static/
    └── js/
        └── charts.js           # NEW

scripts/
└── init_db.py                  # UPDATE - add dummy data

docs/
└── ticket-03/
    ├── IMPLEMENTATION_PLAN.md  # THIS FILE
    └── USER_GUIDE.md           # NEW
```

---

## Implementation Order (Recommended)

### Day 1: Financial Module Foundation
1. Create Payment and Expense models
2. Run database migrations
3. Implement PaymentService and ExpenseService
4. Test services with basic data

### Day 2: Financial Module Frontend
5. Create parent payment forms and history view
6. Create manager expense forms and list view
7. Implement FinancialReportService
8. Create manager financial report page
9. Test complete financial workflow

### Day 3: Maintenance Module
10. Create MaintenanceTask model
11. Run database migration
12. Implement MaintenanceService
13. Create manager maintenance dashboard
14. Create worker task views
15. Test complete maintenance workflow

### Day 4: Dashboards & Charts
16. Enhance manager dashboard
17. Enhance parent dashboard
18. Enhance worker dashboard
19. Implement Chart.js visualizations
20. Update navigation menus

### Day 5: Testing & Documentation
21. Run comprehensive testing checklist
22. Fix bugs and edge cases
23. Update documentation
24. Final UI polish
25. Update dummy data script

---

## Acceptance Criteria Validation

Before marking ticket-03 as complete, verify:

### Functional Requirements
- [x] **Data Persistence**: All financial and maintenance data persists through DB layer
- [x] **Financial Tracking**: Parents can record payments; Managers can view income/expense reports
- [x] **Maintenance Tasks**: Managers assign tasks; Workers update status; Teachers/Workers report issues
- [x] **Reports**: Manager dashboard shows students per course, queues, open tasks, budget
- [x] **Reports**: Parent dashboard shows child progress and payments
- [x] **Reports**: Worker dashboard shows assigned tasks
- [x] **Web UI**: All features accessible via web pages (no CLI required)

### Technical Requirements
- [x] **OOP**: All new classes follow OOP principles from Ticket 1
- [x] **3-Layer Architecture**: Data → Business Logic → Frontend maintained
- [x] **Error Handling**: Try/except blocks with user-friendly messages
- [x] **Documentation**: All classes and methods documented

### Quality Checks
- [x] No broken links or 404 errors
- [x] All forms validate inputs
- [x] All database operations use transactions properly
- [x] No security vulnerabilities (SQL injection, XSS)
- [x] Responsive design works on mobile
- [x] Code follows project conventions

---

## Dependencies & Prerequisites

### Assumed Complete from Tickets 1 & 2:
- User model with Manager, Parent, Teacher, Student, Worker subclasses
- Course model and CRUD operations
- Enrollment model and service
- Queue model and auto-enrollment logic
- Authentication system (Flask-Login or similar)
- Role-based access control decorators
- Base templates with navigation
- Dashboard stubs for each role

### Required Before Starting:
- Database connection working
- SQLAlchemy models can be created
- Alembic migrations working
- Bootstrap CSS loaded in templates
- Flask-WTF forms working (if using)
- Current user context available in templates

---

## Troubleshooting Guide

### Common Issues

**Issue**: Migration fails with foreign key errors
**Solution**: Ensure User and Course models exist before creating Payment/MaintenanceTask models

**Issue**: Payment amount shows incorrect decimal places
**Solution**: Use `db.Numeric(10, 2)` for currency fields, format in templates: `{{ "%.2f"|format(amount) }}`

**Issue**: Charts not rendering
**Solution**: Ensure Chart.js loaded, check browser console for errors, verify data format

**Issue**: Worker can't see assigned tasks
**Solution**: Check user_type is 'worker', verify foreign key relationship in MaintenanceTask model

**Issue**: Financial report showing wrong totals
**Solution**: Check date range filtering, ensure timezone handling consistent

---

## Questions for Clarification

Before implementation, please confirm:

1. **Payment Receipt Numbers**: Should they be auto-generated or manual entry?
   - Suggested: Auto-generate as "RCP-YYYYMMDD-XXX"

2. **Expense Categories**: Are the suggested categories sufficient?
   - Salary, Maintenance, Utilities, Supplies, Other
   - Or do you need specific categories?

3. **Maintenance Task Notifications**: Should workers receive notifications when assigned?
   - Email notifications?
   - In-app notifications only?
   - No notifications (just dashboard)?

4. **Financial Report Export**: Do you need CSV/PDF export functionality?
   - Required or optional for future?

5. **Date Range Defaults**: What should financial report show by default?
   - Current month?
   - Last 30 days?
   - User must select range?

6. **Task Reassignment**: Can managers reassign tasks from one worker to another?
   - Yes/No?

7. **Payment Validation**: Should system check if payment amount matches course price?
   - Strict validation?
   - Allow partial payments?
   - Allow any amount?

8. **Expense Approval Workflow**: Do expenses need approval, or are they final when created?
   - Final when created (simpler)
   - Need approval workflow (more complex)

9. **Maintenance Task Comments**: Should there be a comment/note thread on tasks?
   - Simple notes field (current plan)
   - Full comment system with history
   - Activity log only

10. **Dashboard Refresh**: Should dashboards auto-refresh or manual refresh only?
    - Manual refresh (simpler)
    - Auto-refresh every X seconds (requires AJAX)

---

## Success Metrics

Ticket-03 is complete when:

1. ✅ All 14 implementation tasks completed
2. ✅ All acceptance criteria met
3. ✅ All test checklist items pass
4. ✅ Documentation updated
5. ✅ No critical bugs
6. ✅ Code reviewed (if team project)
7. ✅ Dummy data script runs successfully
8. ✅ System meets all original requirements from project brief

---

## Next Steps After Completion

1. **User Acceptance Testing**: Have end users test the system
2. **Performance Testing**: Test with larger datasets
3. **Security Audit**: Review authentication and authorization
4. **Deployment Preparation**: Set up production environment
5. **Training Materials**: Create user training guides
6. **Maintenance Plan**: Document ongoing maintenance procedures

---

**End of Implementation Plan**

*Review this plan, answer the clarification questions, and begin implementation following the recommended order.*
