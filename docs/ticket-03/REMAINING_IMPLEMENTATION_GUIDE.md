# Ticket-03 Remaining Implementation Guide

This document provides ready-to-use code snippets for completing the remaining parts of Ticket-03.

---

## 1. Parent Payment Routes

Add these routes to `app/routers/parent_routes.py`:

```python
from app.models.payment import PaymentType, PaymentMethod
from app.services.payment_service import PaymentService
from decimal import Decimal

# ============================================================================
# PAYMENT ROUTES
# ============================================================================

@router.get("/payments", response_class=HTMLResponse)
async def view_payments(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Display parent's payment history."""
    try:
        require_parent(current_user)

        # Get payment summary and history
        payments = PaymentService.get_parent_payments(db, current_user.id)
        summary = PaymentService.get_payment_summary(db, current_user.id)

        return templates.TemplateResponse(
            "parent/payments.html",
            {
                "request": request,
                "user": current_user,
                "payments": payments,
                "summary": summary
            }
        )
    except HTTPException:
        return RedirectResponse(url="/login", status_code=302)


@router.get("/payments/create", response_class=HTMLResponse)
async def create_payment_form(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Display payment creation form."""
    try:
        require_parent(current_user)

        # Get parent's children
        children = UserService.get_parent_children(current_user.id, db)

        # Get all courses
        courses = CourseService.get_all_courses(db)

        # Get messages
        success = request.session.pop("success", None)
        error = request.session.pop("error", None)

        return templates.TemplateResponse(
            "parent/payment_create.html",
            {
                "request": request,
                "user": current_user,
                "children": children,
                "courses": courses,
                "success": success,
                "error": error
            }
        )
    except HTTPException:
        return RedirectResponse(url="/login", status_code=302)


@router.post("/payments/create")
async def create_payment(
    request: Request,
    course_id: int = Form(...),
    amount: str = Form(...),
    payment_method: str = Form(...),
    notes: str = Form(""),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Submit new payment."""
    try:
        require_parent(current_user)

        # Validate and create payment
        try:
            amount_decimal = Decimal(amount)
            method = PaymentMethod(payment_method)

            PaymentService.record_payment(
                db,
                payer_id=current_user.id,
                amount=amount_decimal,
                payment_type=PaymentType.TUITION,
                payment_method=method,
                reference_id=course_id,
                notes=notes if notes else None
            )

            request.session["success"] = "Payment recorded successfully!"
            return RedirectResponse(url="/parent/payments", status_code=302)

        except ValueError as e:
            request.session["error"] = f"Invalid payment data: {str(e)}"
            return RedirectResponse(url="/parent/payments/create", status_code=302)

    except HTTPException:
        return RedirectResponse(url="/login", status_code=302)
```

---

## 2. Manager Financial & Maintenance Routes

Add these routes to `app/routers/manager_routes.py`:

```python
from app.models.expense import ExpenseCategory
from app.models.maintenance_task import TaskPriority, TaskStatus
from app.services.expense_service import ExpenseService
from app.services.maintenance_service import MaintenanceService
from app.services.financial_report_service import FinancialReportService
from datetime import date, timedelta

# ============================================================================
# FINANCIAL ROUTES
# ============================================================================

@router.get("/financial-report", response_class=HTMLResponse)
async def financial_report(
    request: Request,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Display financial report with charts."""
    try:
        require_manager(current_user)

        # Default to current month if no dates provided
        if not start_date or not end_date:
            today = date.today()
            start = date(today.year, today.month, 1)
            if today.month == 12:
                end = date(today.year + 1, 1, 1) - timedelta(days=1)
            else:
                end = date(today.year, today.month + 1, 1) - timedelta(days=1)
        else:
            start = date.fromisoformat(start_date)
            end = date.fromisoformat(end_date)

        # Generate financial summary
        summary = FinancialReportService.generate_financial_summary(db, start, end)

        return templates.TemplateResponse(
            "manager/financial_report.html",
            {
                "request": request,
                "user": current_user,
                "summary": summary,
                "start_date": start,
                "end_date": end
            }
        )
    except HTTPException:
        return RedirectResponse(url="/login", status_code=302)


@router.get("/expenses", response_class=HTMLResponse)
async def list_expenses(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Display list of all expenses."""
    try:
        require_manager(current_user)

        expenses = ExpenseService.get_expenses(db)

        return templates.TemplateResponse(
            "manager/expenses.html",
            {
                "request": request,
                "user": current_user,
                "expenses": expenses
            }
        )
    except HTTPException:
        return RedirectResponse(url="/login", status_code=302)


@router.get("/expenses/create", response_class=HTMLResponse)
async def create_expense_form(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Display expense creation form."""
    try:
        require_manager(current_user)

        success = request.session.pop("success", None)
        error = request.session.pop("error", None)

        return templates.TemplateResponse(
            "manager/expense_create.html",
            {
                "request": request,
                "user": current_user,
                "success": success,
                "error": error
            }
        )
    except HTTPException:
        return RedirectResponse(url="/login", status_code=302)


@router.post("/expenses/create")
async def create_expense(
    request: Request,
    category: str = Form(...),
    amount: str = Form(...),
    expense_date: str = Form(...),
    description: str = Form(""),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Submit new expense."""
    try:
        require_manager(current_user)

        try:
            cat = ExpenseCategory(category)
            amt = Decimal(amount)
            exp_date = date.fromisoformat(expense_date)

            ExpenseService.create_expense(
                db,
                category=cat,
                amount=amt,
                expense_date=exp_date,
                description=description if description else None,
                manager_id=current_user.id
            )

            request.session["success"] = "Expense recorded successfully!"
            return RedirectResponse(url="/manager/expenses", status_code=302)

        except ValueError as e:
            request.session["error"] = f"Invalid expense data: {str(e)}"
            return RedirectResponse(url="/manager/expenses/create", status_code=302)

    except HTTPException:
        return RedirectResponse(url="/login", status_code=302)


# ============================================================================
# MAINTENANCE ROUTES
# ============================================================================

@router.get("/maintenance", response_class=HTMLResponse)
async def list_maintenance_tasks(
    request: Request,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Display all maintenance tasks."""
    try:
        require_manager(current_user)

        # Get tasks based on status filter
        if status:
            try:
                task_status = TaskStatus(status)
                tasks = MaintenanceService.get_tasks_by_status(db, task_status)
            except ValueError:
                tasks = MaintenanceService.get_all_tasks(db)
        else:
            tasks = MaintenanceService.get_all_tasks(db)

        # Get workers for assignment
        workers = UserService.get_users_by_role(UserRole.WORKER, db)

        # Get statistics
        stats = MaintenanceService.get_task_statistics(db)

        return templates.TemplateResponse(
            "manager/maintenance.html",
            {
                "request": request,
                "user": current_user,
                "tasks": tasks,
                "workers": workers,
                "stats": stats,
                "current_status": status
            }
        )
    except HTTPException:
        return RedirectResponse(url="/login", status_code=302)


@router.get("/maintenance/create", response_class=HTMLResponse)
async def create_maintenance_task_form(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Display maintenance task creation form."""
    try:
        require_manager(current_user)

        workers = UserService.get_users_by_role(UserRole.WORKER, db)

        success = request.session.pop("success", None)
        error = request.session.pop("error", None)

        return templates.TemplateResponse(
            "manager/maintenance_create.html",
            {
                "request": request,
                "user": current_user,
                "workers": workers,
                "success": success,
                "error": error
            }
        )
    except HTTPException:
        return RedirectResponse(url="/login", status_code=302)


@router.post("/maintenance/create")
async def create_maintenance_task(
    request: Request,
    title: str = Form(...),
    description: str = Form(""),
    priority: str = Form(...),
    worker_id: Optional[int] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Submit new maintenance task."""
    try:
        require_manager(current_user)

        try:
            task_priority = TaskPriority(priority)

            task = MaintenanceService.create_task(
                db,
                title=title,
                description=description if description else None,
                priority=task_priority,
                reported_by_user_id=current_user.id
            )

            # Assign to worker if specified
            if worker_id:
                MaintenanceService.assign_task(db, task.id, worker_id, current_user.id)

            request.session["success"] = "Maintenance task created successfully!"
            return RedirectResponse(url="/manager/maintenance", status_code=302)

        except ValueError as e:
            request.session["error"] = f"Error creating task: {str(e)}"
            return RedirectResponse(url="/manager/maintenance/create", status_code=302)

    except HTTPException:
        return RedirectResponse(url="/login", status_code=302)


@router.post("/maintenance/{task_id}/assign")
async def assign_maintenance_task(
    request: Request,
    task_id: int,
    worker_id: int = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Assign task to a worker."""
    try:
        require_manager(current_user)

        try:
            MaintenanceService.assign_task(db, task_id, worker_id, current_user.id)
            request.session["success"] = "Task assigned successfully!"
        except ValueError as e:
            request.session["error"] = str(e)

        return RedirectResponse(url="/manager/maintenance", status_code=302)

    except HTTPException:
        return RedirectResponse(url="/login", status_code=302)
```

---

## 3. Update Seed Data Script

Add to `scripts/seed_data.py`:

```python
from app.models.payment import Payment, PaymentType, PaymentMethod, PaymentStatus
from app.models.expense import Expense, ExpenseCategory
from app.models.maintenance_task import MaintenanceTask, TaskPriority, TaskStatus
from datetime import date, timedelta
from decimal import Decimal

def seed_financial_data(db):
    """Seed payment and expense data."""
    print("Seeding financial data...")

    # Sample payments
    payments = [
        Payment(
            payer_id=4,  # Parent 1
            amount=Decimal("150.00"),
            payment_type=PaymentType.TUITION,
            payment_method=PaymentMethod.CARD,
            payment_date=datetime.utcnow() - timedelta(days=15),
            status=PaymentStatus.COMPLETED,
            reference_id=1,  # Course 1
            notes="Payment for Math course"
        ),
        Payment(
            payer_id=4,
            amount=Decimal("200.00"),
            payment_type=PaymentType.TUITION,
            payment_method=PaymentMethod.CASH,
            payment_date=datetime.utcnow() - timedelta(days=10),
            status=PaymentStatus.COMPLETED,
            reference_id=2,
            notes="Payment for Science course"
        ),
        # Add more payments...
    ]

    # Sample expenses
    expenses = [
        Expense(
            category=ExpenseCategory.SALARY,
            amount=Decimal("2000.00"),
            expense_date=date.today() - timedelta(days=30),
            description="Teacher salary - October",
            created_by_manager_id=1
        ),
        Expense(
            category=ExpenseCategory.UTILITIES,
            amount=Decimal("350.00"),
            expense_date=date.today() - timedelta(days=20),
            description="Electricity bill",
            created_by_manager_id=1
        ),
        # Add more expenses...
    ]

    db.bulk_save_objects(payments)
    db.bulk_save_objects(expenses)
    db.commit()


def seed_maintenance_data(db):
    """Seed maintenance task data."""
    print("Seeding maintenance data...")

    tasks = [
        MaintenanceTask(
            title="Fix broken chair in Room 101",
            description="Chair leg is broken, needs repair or replacement",
            priority=TaskPriority.MEDIUM,
            status=TaskStatus.PENDING,
            reported_by_user_id=2,  # Teacher
            created_at=datetime.utcnow() - timedelta(days=5)
        ),
        MaintenanceTask(
            title="AC not working in Room 203",
            description="Air conditioning unit not cooling properly",
            priority=TaskPriority.HIGH,
            status=TaskStatus.IN_PROGRESS,
            assigned_to_worker_id=6,  # Worker 1
            reported_by_user_id=1,  # Manager
            started_at=datetime.utcnow() - timedelta(days=2),
            created_at=datetime.utcnow() - timedelta(days=3)
        ),
        MaintenanceTask(
            title="Replace broken window",
            description="Window in hallway is cracked",
            priority=TaskPriority.URGENT,
            status=TaskStatus.PENDING,
            reported_by_user_id=6,  # Worker reporting issue
            created_at=datetime.utcnow() - timedelta(days=1)
        ),
        # Add more tasks...
    ]

    db.bulk_save_objects(tasks)
    db.commit()

# Call these functions in the main seed_database() function:
# seed_financial_data(db)
# seed_maintenance_data(db)
```

---

## 4. Basic Template Examples

### Parent Payment Template (`templates/parent/payments.html`)

```html
{% extends "base.html" %}

{% block content %}
<div class="container mx-auto px-4 py-8">
    <h1 class="text-3xl font-bold mb-6">Payment History</h1>

    <!-- Payment Summary -->
    <div class="bg-white rounded-lg shadow p-6 mb-6">
        <h2 class="text-xl font-semibold mb-4">Summary</h2>
        <div class="grid grid-cols-2 gap-4">
            <div>
                <p class="text-gray-600">Total Payments</p>
                <p class="text-2xl font-bold">{{ summary.payment_count }}</p>
            </div>
            <div>
                <p class="text-gray-600">Total Amount</p>
                <p class="text-2xl font-bold">${{ "%.2f"|format(summary.total_paid) }}</p>
            </div>
        </div>
    </div>

    <!-- Payment List -->
    <div class="bg-white rounded-lg shadow overflow-hidden">
        <table class="min-w-full">
            <thead class="bg-gray-50">
                <tr>
                    <th class="px-6 py-3 text-left">Date</th>
                    <th class="px-6 py-3 text-left">Amount</th>
                    <th class="px-6 py-3 text-left">Method</th>
                    <th class="px-6 py-3 text-left">Notes</th>
                </tr>
            </thead>
            <tbody>
                {% for payment in payments %}
                <tr class="border-t">
                    <td class="px-6 py-4">{{ payment.payment_date.strftime('%Y-%m-%d') }}</td>
                    <td class="px-6 py-4">${{ "%.2f"|format(payment.amount) }}</td>
                    <td class="px-6 py-4">{{ payment.payment_method.value }}</td>
                    <td class="px-6 py-4">{{ payment.notes or '-' }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>

    <div class="mt-6">
        <a href="/parent/payments/create" class="bg-blue-500 text-white px-6 py-2 rounded hover:bg-blue-600">
            Make Payment
        </a>
    </div>
</div>
{% endblock %}
```

### Manager Financial Report Template (`templates/manager/financial_report.html`)

```html
{% extends "base.html" %}

{% block content %}
<div class="container mx-auto px-4 py-8">
    <h1 class="text-3xl font-bold mb-6">Financial Report</h1>

    <!-- Date Range Filter -->
    <form method="get" class="mb-6">
        <div class="flex gap-4">
            <input type="date" name="start_date" value="{{ start_date }}" class="border rounded px-4 py-2">
            <input type="date" name="end_date" value="{{ end_date }}" class="border rounded px-4 py-2">
            <button type="submit" class="bg-blue-500 text-white px-6 py-2 rounded">Filter</button>
        </div>
    </form>

    <!-- Summary Cards -->
    <div class="grid grid-cols-3 gap-6 mb-8">
        <div class="bg-green-50 rounded-lg shadow p-6">
            <h3 class="text-lg font-semibold text-green-800">Total Income</h3>
            <p class="text-3xl font-bold text-green-600">${{ "%.2f"|format(summary.total_income) }}</p>
        </div>
        <div class="bg-red-50 rounded-lg shadow p-6">
            <h3 class="text-lg font-semibold text-red-800">Total Expenses</h3>
            <p class="text-3xl font-bold text-red-600">${{ "%.2f"|format(summary.total_expenses) }}</p>
        </div>
        <div class="bg-blue-50 rounded-lg shadow p-6">
            <h3 class="text-lg font-semibold text-blue-800">Net Result</h3>
            <p class="text-3xl font-bold {{ 'text-green-600' if summary.net_result > 0 else 'text-red-600' }}">
                ${{ "%.2f"|format(summary.net_result) }}
            </p>
        </div>
    </div>

    <!-- Charts Section -->
    <div class="grid grid-cols-2 gap-6">
        <div class="bg-white rounded-lg shadow p-6">
            <h3 class="text-xl font-semibold mb-4">Income by Course</h3>
            <canvas id="incomeChart"></canvas>
        </div>
        <div class="bg-white rounded-lg shadow p-6">
            <h3 class="text-xl font-semibold mb-4">Expenses by Category</h3>
            <canvas id="expensesChart"></canvas>
        </div>
    </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0"></script>
<script>
    // Income by Course Chart
    const incomeData = {{ summary.income_by_course | tojson }};
    new Chart(document.getElementById('incomeChart'), {
        type: 'pie',
        data: {
            labels: incomeData.map(d => d.course_name),
            datasets: [{
                data: incomeData.map(d => d.total_income),
                backgroundColor: ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6']
            }]
        }
    });

    // Expenses by Category Chart
    const expenseData = {{ summary.expenses_by_category | tojson }};
    new Chart(document.getElementById('expensesChart'), {
        type: 'doughnut',
        data: {
            labels: expenseData.map(d => d.category_display),
            datasets: [{
                data: expenseData.map(d => d.total_amount),
                backgroundColor: ['#EF4444', '#F59E0B', '#10B981', '#3B82F6', '#8B5CF6']
            }]
        }
    });
</script>
{% endblock %}
```

---

## 5. Testing Checklist

After implementing the above:

- [ ] Database resets without errors
- [ ] Worker can view assigned tasks
- [ ] Worker can update task status
- [ ] Worker can report issues
- [ ] Parent can view payment history
- [ ] Parent can create new payment
- [ ] Manager can view financial report with charts
- [ ] Manager can create expenses
- [ ] Manager can view maintenance tasks
- [ ] Manager can create and assign tasks
- [ ] All dashboards load correctly

---

## 6. Quick Test Commands

```bash
# Reset database with new models
uv run python scripts/reset_db.py

# Start server
uv run uvicorn app.main:app --reload

# Test in browser
# http://localhost:8000
# Login as: worker1 / password123
# Login as: parent1 / password123
# Login as: manager1 / password123
```

---

**This guide should help complete the remaining 50% of ticket-03 implementation.**
