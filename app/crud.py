"""
crud.py
-------
Database operations (Create, Read, Update, Delete) for Student records.
Separates data access logic from HTTP route handlers.
"""

from datetime import date
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app import models, schemas


def get_student_by_student_id(db: Session, student_id: str) -> Optional[models.Student]:
    """
    Retrieve a single student by their unique student_id (e.g., 'STU-1001').
    Also checks primary key 'id' if student_id is numeric as a fallback.
    """
    student = db.query(models.Student).filter(models.Student.student_id == student_id).first()
    if not student and student_id.isdigit():
        student = db.query(models.Student).filter(models.Student.id == int(student_id)).first()
    return student


def get_student_by_email(db: Session, email: str) -> Optional[models.Student]:
    """Check if a student with the given email already exists."""
    return db.query(models.Student).filter(models.Student.email == email.lower()).first()


def get_students(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    course: Optional[str] = None
) -> List[models.Student]:
    """
    List students with optional search filtering by name/student_id and course,
    with pagination support via skip and limit.
    """
    query = db.query(models.Student)

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                models.Student.name.ilike(search_term),
                models.Student.student_id.ilike(search_term)
            )
        )

    if course:
        query = query.filter(models.Student.course.ilike(f"%{course}%"))

    return query.order_by(models.Student.id.asc()).offset(skip).limit(limit).all()


def get_all_students_for_ai(db: Session) -> List[models.Student]:
    """Retrieve all student records to format as context for the AI query."""
    return db.query(models.Student).order_by(models.Student.id.asc()).all()


def create_student(db: Session, student_in: schemas.StudentCreate) -> models.Student:
    """
    Create a new student record in the SQLite database.
    If enrollment_date is omitted, defaults to today's date (YYYY-MM-DD).
    """
    enrollment = student_in.enrollment_date
    if not enrollment:
        enrollment = date.today().isoformat()

    db_student = models.Student(
        student_id=student_in.student_id.strip(),
        name=student_in.name.strip(),
        date_of_birth=student_in.date_of_birth.strip(),
        email=student_in.email.strip().lower(),
        phone=student_in.phone.strip(),
        course=student_in.course.strip() if student_in.course else None,
        address=student_in.address.strip() if student_in.address else None,
        enrollment_date=enrollment
    )

    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student


def update_student(
    db: Session,
    db_student: models.Student,
    student_update: schemas.StudentUpdate
) -> models.Student:
    """
    Update an existing student's attributes.
    Supports both partial (PATCH) and full (PUT) update payloads.
    """
    update_data = student_update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        if value is not None and isinstance(value, str):
            value = value.strip()
            if field == "email":
                value = value.lower()
        setattr(db_student, field, value)

    db.commit()
    db.refresh(db_student)
    return db_student


def delete_student(db: Session, db_student: models.Student) -> None:
    """Delete a student record from the database."""
    db.delete(db_student)
    db.commit()
