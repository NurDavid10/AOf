"""
Main FastAPI application entry point.

This module initializes the FastAPI application, sets up routes,
templates, and handles authentication.
"""

from fastapi import FastAPI, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware
from pathlib import Path

from app.database import get_db
from app.config import get_settings
from app.services.auth_service import AuthService
from app.services.demo_user_service import init_demo_users
from app.models.user import User
from app.dependencies.auth import get_current_user
from app.routers import manager_routes, parent_routes, worker_routes

# Initialize FastAPI app
app = FastAPI(
    title="Academic Tomorrow Learning Center",
    description="Learning Center Management System",
    version="0.1.0"
)

# Get settings
settings = get_settings()

# Add session middleware
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

# Mount static files
static_path = Path(__file__).parent / "static"
static_path.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Set up templates
templates_path = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(templates_path))

# Include routers
app.include_router(manager_routes.router)
app.include_router(parent_routes.router)
app.include_router(worker_routes.router)


# Startup event: Initialize demo users
@app.on_event("startup")
async def startup_event():
    """
    Initialize demo users on application startup.
    
    This ensures that demo users (manager1, teacher1, student1, parent1, worker1)
    exist in the database with password 'password123' whenever the app starts.
    """
    init_demo_users()


# Root route - redirect to login page
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """
    Root route that redirects to the login page.

    Returns:
        RedirectResponse: Redirects to login page
    """
    return RedirectResponse(url="/login", status_code=302)


# Login page
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """
    Display the login page.

    Returns:
        HTMLResponse: Login page template
    """
    error = request.session.pop("error", None)
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "error": error}
    )


# Login processing
@app.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Process login form submission.

    Args:
        request: FastAPI request object
        username: Username from form
        password: Password from form
        db: Database session

    Returns:
        RedirectResponse: Redirects to dashboard or back to login
    """
    try:
        # Authenticate user
        user = AuthService.authenticate_user(username, password, db)

        if not user:
            request.session["error"] = "Invalid username or password"
            return RedirectResponse(url="/login", status_code=302)

        # Store user ID and role in session
        request.session["user_id"] = user.id
        request.session["user_role"] = user.role.value
        request.session["username"] = user.username
        request.session["full_name"] = user.full_name or user.username

        # Redirect to role-specific dashboard
        dashboard_route = AuthService.get_dashboard_route(user)
        return RedirectResponse(url=dashboard_route, status_code=302)

    except Exception as e:
        request.session["error"] = f"Login error: {str(e)}"
        return RedirectResponse(url="/login", status_code=302)


# Logout
@app.get("/logout")
async def logout(request: Request):
    """
    Log out the current user.

    Returns:
        RedirectResponse: Redirects to login page
    """
    request.session.clear()
    return RedirectResponse(url="/login", status_code=302)


# Dashboard route - redirects to role-specific dashboard
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    """
    General dashboard that redirects to role-specific dashboard.

    Returns:
        RedirectResponse: Redirects to role-specific dashboard
    """
    try:
        user = get_current_user(request, db)
        dashboard_route = AuthService.get_dashboard_route(user)
        return RedirectResponse(url=dashboard_route, status_code=302)
    except HTTPException:
        return RedirectResponse(url="/login", status_code=302)


# Manager dashboard
@app.get("/manager/dashboard", response_class=HTMLResponse)
async def manager_dashboard(request: Request, db: Session = Depends(get_db)):
    """Manager dashboard."""
    try:
        user = get_current_user(request, db)
        if user.role.value != "manager":
            raise HTTPException(status_code=403, detail="Access denied")

        return templates.TemplateResponse(
            "manager/dashboard.html",
            {"request": request, "user": user}
        )
    except HTTPException:
        return RedirectResponse(url="/login", status_code=302)


# Teacher dashboard
@app.get("/teacher/dashboard", response_class=HTMLResponse)
async def teacher_dashboard(request: Request, db: Session = Depends(get_db)):
    """Teacher dashboard."""
    try:
        user = get_current_user(request, db)
        if user.role.value != "teacher":
            raise HTTPException(status_code=403, detail="Access denied")

        return templates.TemplateResponse(
            "teacher/dashboard.html",
            {"request": request, "user": user}
        )
    except HTTPException:
        return RedirectResponse(url="/login", status_code=302)


# Student dashboard
@app.get("/student/dashboard", response_class=HTMLResponse)
async def student_dashboard(request: Request, db: Session = Depends(get_db)):
    """Student dashboard."""
    try:
        user = get_current_user(request, db)
        if user.role.value != "student":
            raise HTTPException(status_code=403, detail="Access denied")

        return templates.TemplateResponse(
            "student/dashboard.html",
            {"request": request, "user": user}
        )
    except HTTPException:
        return RedirectResponse(url="/login", status_code=302)


# Parent dashboard
@app.get("/parent/dashboard", response_class=HTMLResponse)
async def parent_dashboard(request: Request, db: Session = Depends(get_db)):
    """Parent dashboard."""
    try:
        user = get_current_user(request, db)
        if user.role.value != "parent":
            raise HTTPException(status_code=403, detail="Access denied")

        return templates.TemplateResponse(
            "parent/dashboard.html",
            {"request": request, "user": user}
        )
    except HTTPException:
        return RedirectResponse(url="/login", status_code=302)


# Worker dashboard is now handled in worker_routes.py


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
