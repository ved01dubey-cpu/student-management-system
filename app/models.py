"""
models.py
---------
SQLAlchemy database models for the Student Management application.
Maps Python classes to SQLite database tables.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Date, DateTime
from app.database import Base


class Student(Base):
    """
    SQLAlchemy model representing the 'students' table in SQLite.
    Stores core student information and optional profile details.
    """
    __tablename__ = "students"

    # Internal primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Unique student identification code (e.g., 'STU-1001')
    student_id = Column(String(50), unique=True, index=True, nullable=False)

    # Core student fields
    name = Column(String(100), nullable=False, index=True)
    date_of_birth = Column(String(20), nullable=False)  # Format: YYYY-MM-DD
    email = Column(String(120), unique=True, index=True, nullable=False)
    phone = Column(String(30), nullable=False)

    # Optional fields
    course = Column(String(100), nullable=True, index=True)
    address = Column(String(255), nullable=True)
    enrollment_date = Column(String(20), nullable=True)  # Format: YYYY-MM-DD

    # Metadata timestamp
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    def __repr__(self):
        return f"<Student(student_id='{self.student_id}', name='{self.name}', course='{self.course}')>"
