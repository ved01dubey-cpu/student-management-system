"""
main.py
-------
Main FastAPI application entry point.
Configures routes, database initialization, error handling, and documentation.
"""

from contextlib import asynccontextmanager
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import engine, Base, get_db
from app import models, schemas, crud
from app.ai_service import ask_ollama, DEFAULT_MODEL


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler:
    Initializes database tables on startup and seeds initial records if empty.
    """
    # Create SQLite database tables if they do not exist
    Base.metadata.create_all(bind=engine)

    # Automatically populate sample student records if table is empty (great for live cloud deployment)
    try:
        from seed_data import SAMPLE_STUDENTS
        db = SessionLocal()
        try:
            if not crud.get_students(db, limit=1):
                for data in SAMPLE_STUDENTS:
                    student_schema = schemas.StudentCreate(**data)
                    crud.create_student(db, student_schema)
        finally:
            db.close()
    except Exception:
        pass

    yield



# Initialize FastAPI app with student-friendly metadata
app = FastAPI(
    title="Student Records Management System API",
    description=(
        "A student records management REST API built with FastAPI and SQLite. "
        "Supports full CRUD operations (Create, Read, Update, Delete) and an "
        "optional Ollama extension to query student data using natural language."
    ),
    version="1.0.0",
    lifespan=lifespan
)


# ---------------------------------------------------------------------------
# Root and Health Check Endpoints
# ---------------------------------------------------------------------------

@app.get(
    "/",
    tags=["Root"],
    summary="API Home & Status",
    description="Returns welcome information and pointers to interactive API documentation."
)
def root():
    return {
        "message": "Welcome to the Student Records Management API!",
        "status": "online",
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "endpoints": {
            "create_student": "POST /students",
            "list_students": "GET /students",
            "get_student": "GET /students/{student_id}",
            "update_student": "PUT /students/{student_id} or PATCH /students/{student_id}",
            "delete_student": "DELETE /students/{student_id}",
            "ask_ai": "POST /students/ask"
        }
    }


# ---------------------------------------------------------------------------
# Student CRUD Endpoints
# ---------------------------------------------------------------------------

@app.post(
    "/students",
    response_model=schemas.StudentResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Students"],
    summary="Create a new student",
    description="Registers a new student record into the SQLite database. Ensures student_id and email are unique."
)
def create_student(
    student_in: schemas.StudentCreate,
    db: Session = Depends(get_db)
):
    # Check if student_id is already in use
    existing_by_id = crud.get_student_by_student_id(db, student_in.student_id)
    if existing_by_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"A student with ID '{student_in.student_id}' already exists."
        )

    # Check if email is already registered
    existing_by_email = crud.get_student_by_email(db, student_in.email)
    if existing_by_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"A student with email '{student_in.email}' already exists."
        )

    return crud.create_student(db=db, student_in=student_in)


@app.get(
    "/students",
    response_model=List[schemas.StudentResponse],
    tags=["Students"],
    summary="List and filter students",
    description="Retrieves a list of students with optional search filters (name/ID, course) and pagination."
)
def list_students(
    search: Optional[str] = Query(
        default=None,
        description="Filter by name or student ID (case-insensitive substring)"
    ),
    course: Optional[str] = Query(
        default=None,
        description="Filter by course name (case-insensitive substring)"
    ),
    skip: int = Query(
        default=0,
        ge=0,
        description="Number of records to skip for pagination"
    ),
    limit: int = Query(
        default=100,
        ge=1,
        le=200,
        description="Maximum number of records to return"
    ),
    db: Session = Depends(get_db)
):
    students = crud.get_students(
        db=db,
        skip=skip,
        limit=limit,
        search=search,
        course=course
    )
    return students


@app.get(
    "/students/{student_id}",
    response_model=schemas.StudentResponse,
    tags=["Students"],
    summary="Get student details",
    description="Retrieve a single student profile by student_id (e.g. 'STU-1001') or numeric database ID."
)
def get_student(
    student_id: str,
    db: Session = Depends(get_db)
):
    student = crud.get_student_by_student_id(db, student_id=student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID '{student_id}' not found."
        )
    return student


@app.put(
    "/students/{student_id}",
    response_model=schemas.StudentResponse,
    tags=["Students"],
    summary="Update student details (Full or Partial)",
    description="Updates the profile details of an existing student record."
)
def update_student_put(
    student_id: str,
    student_update: schemas.StudentUpdate,
    db: Session = Depends(get_db)
):
    student = crud.get_student_by_student_id(db, student_id=student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID '{student_id}' not found."
        )

    # If updating email, check that the new email doesn't collide with another student
    if student_update.email and student_update.email.lower() != student.email.lower():
        conflict = crud.get_student_by_email(db, student_update.email)
        if conflict:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Email '{student_update.email}' is already used by another student."
            )

    return crud.update_student(db=db, db_student=student, student_update=student_update)


@app.patch(
    "/students/{student_id}",
    response_model=schemas.StudentResponse,
    tags=["Students"],
    summary="Partially update student details",
    description="Updates specific fields of an existing student record."
)
def update_student_patch(
    student_id: str,
    student_update: schemas.StudentUpdate,
    db: Session = Depends(get_db)
):
    # Patch shares the same logic as Put since StudentUpdate allows all fields to be optional
    return update_student_put(student_id=student_id, student_update=student_update, db=db)


@app.delete(
    "/students/{student_id}",
    response_model=schemas.MessageResponse,
    tags=["Students"],
    summary="Delete a student",
    description="Removes a student record from the SQLite database permanently."
)
def delete_student(
    student_id: str,
    db: Session = Depends(get_db)
):
    student = crud.get_student_by_student_id(db, student_id=student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID '{student_id}' not found."
        )

    deleted_id = student.student_id
    deleted_name = student.name
    crud.delete_student(db=db, db_student=student)

    return schemas.MessageResponse(
        message=f"Student record '{deleted_id}' ({deleted_name}) was successfully deleted."
    )


# ---------------------------------------------------------------------------
# Optional Ollama AI Extension Endpoint
# ---------------------------------------------------------------------------

@app.post(
    "/students/ask",
    response_model=schemas.AskAIResponse,
    tags=["AI Extension (Ollama)"],
    summary="Ask questions about students using natural language",
    description=(
        "Uses a local Ollama instance (e.g. LLaMA 3) to answer natural language questions "
        "about current student records stored in SQLite."
    )
)
async def ask_students_ai(
    request: schemas.AskAIRequest,
    db: Session = Depends(get_db)
):
    students = crud.get_all_students_for_ai(db)
    model_name = request.model or DEFAULT_MODEL
    
    answer = await ask_ollama(
        question=request.question,
        students=students,
        model_name=model_name
    )

    return schemas.AskAIResponse(
        question=request.question,
        answer=answer,
        students_in_context=len(students),
        model_used=model_name
    )
