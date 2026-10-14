"""
schemas.py
----------
Pydantic schemas for data validation and serialization.
Defines the structure of request bodies and response formats.
"""

import re
from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict


EMAIL_REGEX = r"^[\w\.\+\-]+@[a-zA-Z0-9\-]+\.[a-zA-Z0-9\-\.]+$"
DATE_REGEX = r"^\d{4}-\d{2}-\d{2}$"


class StudentBase(BaseModel):
    """Base schema sharing common student attributes."""
    student_id: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="Unique student identifier (e.g. STU-1001)",
        examples=["STU-1001"]
    )
    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Full legal name of the student",
        examples=["Alice Johnson"]
    )
    date_of_birth: str = Field(
        ...,
        description="Birth date in YYYY-MM-DD format",
        examples=["2003-05-15"]
    )
    email: str = Field(
        ...,
        description="Student contact email address",
        examples=["alice.johnson@example.edu"]
    )
    phone: str = Field(
        ...,
        min_length=7,
        max_length=25,
        description="Primary phone or mobile number",
        examples=["+1-555-0199"]
    )
    course: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Enrolled program or course of study",
        examples=["Computer Science"]
    )
    address: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Residential / mailing address",
        examples=["123 University Ave, Room 4B, Cityville"]
    )
    enrollment_date: Optional[str] = Field(
        default=None,
        description="Date of enrollment in YYYY-MM-DD format (defaults to today if empty)",
        examples=["2024-09-01"]
    )

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, value: str) -> str:
        value = value.strip().lower()
        if not re.match(EMAIL_REGEX, value):
            raise ValueError("Invalid email address format (expected e.g. student@school.edu)")
        return value

    @field_validator("date_of_birth")
    @classmethod
    def validate_dob_format(cls, value: str) -> str:
        value = value.strip()
        if not re.match(DATE_REGEX, value):
            raise ValueError("Invalid date_of_birth format. Expected 'YYYY-MM-DD' (e.g., '2003-05-15')")
        return value

    @field_validator("enrollment_date")
    @classmethod
    def validate_enrollment_format(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        value = value.strip()
        if value and not re.match(DATE_REGEX, value):
            raise ValueError("Invalid enrollment_date format. Expected 'YYYY-MM-DD' (e.g., '2024-09-01')")
        return value


class StudentCreate(StudentBase):
    """Schema for creating a new student record."""
    pass


class StudentUpdate(BaseModel):
    """
    Schema for updating an existing student.
    All fields are optional to support both full (PUT) and partial (PATCH) updates.
    """
    name: Optional[str] = Field(default=None, min_length=2, max_length=100)
    date_of_birth: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = Field(default=None, min_length=7, max_length=25)
    course: Optional[str] = Field(default=None, max_length=100)
    address: Optional[str] = Field(default=None, max_length=255)
    enrollment_date: Optional[str] = None

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, value: Optional[str]) -> Optional[str]:
        if value is not None:
            value = value.strip().lower()
            if not re.match(EMAIL_REGEX, value):
                raise ValueError("Invalid email address format")
        return value

    @field_validator("date_of_birth")
    @classmethod
    def validate_dob_format(cls, value: Optional[str]) -> Optional[str]:
        if value is not None:
            value = value.strip()
            if not re.match(DATE_REGEX, value):
                raise ValueError("Invalid date_of_birth format. Expected 'YYYY-MM-DD'")
        return value

    @field_validator("enrollment_date")
    @classmethod
    def validate_enrollment_format(cls, value: Optional[str]) -> Optional[str]:
        if value is not None:
            value = value.strip()
            if not re.match(DATE_REGEX, value):
                raise ValueError("Invalid enrollment_date format. Expected 'YYYY-MM-DD'")
        return value


class StudentResponse(StudentBase):
    """Schema returned to clients when retrieving student details."""
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MessageResponse(BaseModel):
    """Standard message response schema (e.g. for deletions)."""
    message: str
    detail: Optional[str] = None


class AskAIRequest(BaseModel):
    """Schema for querying Ollama regarding student data."""
    question: str = Field(
        ...,
        min_length=3,
        description="Natural language question to ask about the students",
        examples=["How many students are studying Computer Science?", "List the names and emails of all students."]
    )
    model: Optional[str] = Field(
        default="llama3",
        description="Ollama model name to use (e.g. llama3, mistral, phi3, qwen2)",
        examples=["llama3"]
    )


class AskAIResponse(BaseModel):
    """Schema for AI query answer."""
    question: str
    answer: str
    students_in_context: int
    model_used: str
