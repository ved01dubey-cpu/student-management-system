"""
seed_data.py
------------
Utility script to populate the SQLite database with realistic sample student records.
Great for testing the API endpoints and querying via the Ollama extension.

Usage:
    python seed_data.py
"""

from app.database import SessionLocal, engine, Base
from app import models, crud, schemas

# Sample student profiles across different degrees and years
SAMPLE_STUDENTS = [
    {
        "student_id": "STU-1001",
        "name": "Alice Johnson",
        "date_of_birth": "2003-05-14",
        "email": "alice.johnson@campus.edu",
        "phone": "+1-555-0101",
        "course": "Computer Science",
        "address": "120 College Park Way, Dorm A, Cityville",
        "enrollment_date": "2022-09-01"
    },
    {
        "student_id": "STU-1002",
        "name": "Bob Smith",
        "date_of_birth": "2002-11-20",
        "email": "bob.smith@campus.edu",
        "phone": "+1-555-0102",
        "course": "Data Science",
        "address": "450 University Ave, Apt 3B, Cityville",
        "enrollment_date": "2021-09-01"
    },
    {
        "student_id": "STU-1003",
        "name": "Clara Chen",
        "date_of_birth": "2004-02-10",
        "email": "clara.chen@campus.edu",
        "phone": "+1-555-0103",
        "course": "Computer Science",
        "address": "88 Science Drive, Cityville",
        "enrollment_date": "2023-09-01"
    },
    {
        "student_id": "STU-1004",
        "name": "David Patel",
        "date_of_birth": "2003-08-30",
        "email": "david.patel@campus.edu",
        "phone": "+1-555-0104",
        "course": "Cybersecurity",
        "address": "77 Security Lane, West Campus",
        "enrollment_date": "2022-09-01"
    },
    {
        "student_id": "STU-1005",
        "name": "Emma Watson",
        "date_of_birth": "2001-12-05",
        "email": "emma.watson@campus.edu",
        "phone": "+1-555-0105",
        "course": "Software Engineering",
        "address": "310 Maple St, Cityville",
        "enrollment_date": "2021-01-15"
    },
    {
        "student_id": "STU-1006",
        "name": "Franklin Miller",
        "date_of_birth": "2004-07-22",
        "email": "franklin.miller@campus.edu",
        "phone": "+1-555-0106",
        "course": "Business Analytics",
        "address": "12 Pine View Heights, Cityville",
        "enrollment_date": "2023-09-01"
    }
]


def seed():
    print("--- Initializing Database Tables ---")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        inserted_count = 0
        for data in SAMPLE_STUDENTS:
            existing = crud.get_student_by_student_id(db, data["student_id"])
            if not existing:
                student_schema = schemas.StudentCreate(**data)
                crud.create_student(db, student_schema)
                print(f"[+] Added student: {data['student_id']} - {data['name']} ({data['course']})")
                inserted_count += 1
            else:
                print(f"[-] Skipped student (already exists): {data['student_id']} - {data['name']}")

        print(f"\nSuccessfully seeded {inserted_count} new student record(s) into SQLite!")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
