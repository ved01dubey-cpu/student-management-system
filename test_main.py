"""
test_main.py
------------
Automated test suite using Pytest and FastAPI TestClient.
Tests all CRUD operations, input validations, error handling, and edge cases
against an isolated in-memory SQLite database.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

# Setup an isolated in-memory SQLite database for test execution
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    """Dependency override providing access to test in-memory database."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Apply dependency override
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_and_teardown_db():
    """Recreate tables before each test for total test isolation."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


# ---------------------------------------------------------------------------
# Test Cases
# ---------------------------------------------------------------------------

def test_root_endpoint():
    """Test API home route returns 200 OK and endpoint directory."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "endpoints" in data


def test_create_student_success():
    """Test successful creation of a student record (POST /students)."""
    payload = {
        "student_id": "STU-2001",
        "name": "Maya Lin",
        "date_of_birth": "2003-04-12",
        "email": "maya.lin@test.edu",
        "phone": "+1-555-9001",
        "course": "Computer Science",
        "address": "404 North Hall",
        "enrollment_date": "2023-09-01"
    }
    response = client.post("/students", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["student_id"] == "STU-2001"
    assert data["name"] == "Maya Lin"
    assert data["email"] == "maya.lin@test.edu"
    assert data["course"] == "Computer Science"
    assert "id" in data
    assert "created_at" in data


def test_create_student_duplicate_id_fails():
    """Test that creating a student with an existing ID returns HTTP 400."""
    payload = {
        "student_id": "STU-2001",
        "name": "Maya Lin",
        "date_of_birth": "2003-04-12",
        "email": "maya.lin@test.edu",
        "phone": "+1-555-9001"
    }
    # First creation should succeed
    res1 = client.post("/students", json=payload)
    assert res1.status_code == 201

    # Second creation with same student_id but different email
    payload_dup = payload.copy()
    payload_dup["email"] = "maya.alt@test.edu"
    res2 = client.post("/students", json=payload_dup)
    assert res2.status_code == 400
    assert "already exists" in res2.json()["detail"]


def test_create_student_duplicate_email_fails():
    """Test that creating a student with an existing email returns HTTP 400."""
    payload1 = {
        "student_id": "STU-2001",
        "name": "Student One",
        "date_of_birth": "2003-01-01",
        "email": "shared@test.edu",
        "phone": "+1-555-1111"
    }
    client.post("/students", json=payload1)

    payload2 = {
        "student_id": "STU-2002",
        "name": "Student Two",
        "date_of_birth": "2003-02-02",
        "email": "shared@test.edu",
        "phone": "+1-555-2222"
    }
    res = client.post("/students", json=payload2)
    assert res.status_code == 400
    assert "already exists" in res.json()["detail"]


def test_create_student_invalid_email_format():
    """Test validation rejection on invalid email format."""
    payload = {
        "student_id": "STU-2003",
        "name": "Bad Email Student",
        "date_of_birth": "2003-01-01",
        "email": "invalid-email-string",
        "phone": "+1-555-3333"
    }
    res = client.post("/students", json=payload)
    assert res.status_code == 422


def test_get_students_list_and_filters():
    """Test listing students and filtering by course and search term."""
    # Seed 3 students
    s1 = {
        "student_id": "STU-3001",
        "name": "Alpha Ray",
        "date_of_birth": "2002-05-10",
        "email": "alpha@test.edu",
        "phone": "+1-555-3001",
        "course": "Mechanical Engineering"
    }
    s2 = {
        "student_id": "STU-3002",
        "name": "Beta Star",
        "date_of_birth": "2003-06-15",
        "email": "beta@test.edu",
        "phone": "+1-555-3002",
        "course": "Computer Science"
    }
    s3 = {
        "student_id": "STU-3003",
        "name": "Gamma Wave",
        "date_of_birth": "2004-07-20",
        "email": "gamma@test.edu",
        "phone": "+1-555-3003",
        "course": "Computer Science"
    }
    for s in [s1, s2, s3]:
        client.post("/students", json=s)

    # 1. List all
    res_all = client.get("/students")
    assert res_all.status_code == 200
    assert len(res_all.json()) == 3

    # 2. Filter by course
    res_cs = client.get("/students?course=Computer")
    assert res_cs.status_code == 200
    data_cs = res_cs.json()
    assert len(data_cs) == 2
    assert all("Computer Science" in s["course"] for s in data_cs)

    # 3. Filter by search query (name)
    res_search = client.get("/students?search=Beta")
    assert res_search.status_code == 200
    data_search = res_search.json()
    assert len(data_search) == 1
    assert data_search[0]["name"] == "Beta Star"


def test_get_student_by_id():
    """Test retrieving a single student by student_id (GET /students/{student_id})."""
    payload = {
        "student_id": "STU-4001",
        "name": "Samantha Green",
        "date_of_birth": "2002-09-19",
        "email": "samantha@test.edu",
        "phone": "+1-555-4001",
        "course": "Information Technology"
    }
    client.post("/students", json=payload)

    # Retrieve by ID
    response = client.get("/students/STU-4001")
    assert response.status_code == 200
    data = response.json()
    assert data["student_id"] == "STU-4001"
    assert data["name"] == "Samantha Green"

    # Retrieve non-existing ID returns 404
    res_not_found = client.get("/students/UNKNOWN-999")
    assert res_not_found.status_code == 404


def test_update_student_details_put_and_patch():
    """Test modifying student details using PUT and PATCH."""
    payload = {
        "student_id": "STU-5001",
        "name": "Oliver Twist",
        "date_of_birth": "2001-10-10",
        "email": "oliver@test.edu",
        "phone": "+1-555-5001",
        "course": "Literature"
    }
    client.post("/students", json=payload)

    # Update with PUT
    put_update = {
        "name": "Oliver Twist Jr.",
        "course": "English Literature"
    }
    res_put = client.put("/students/STU-5001", json=put_update)
    assert res_put.status_code == 200
    data_put = res_put.json()
    assert data_put["name"] == "Oliver Twist Jr."
    assert data_put["course"] == "English Literature"
    assert data_put["email"] == "oliver@test.edu"  # Unchanged

    # Update with PATCH
    patch_update = {
        "phone": "+1-555-9999"
    }
    res_patch = client.patch("/students/STU-5001", json=patch_update)
    assert res_patch.status_code == 200
    assert res_patch.json()["phone"] == "+1-555-9999"


def test_delete_student():
    """Test removing a student record (DELETE /students/{student_id})."""
    payload = {
        "student_id": "STU-6001",
        "name": "Temporary Student",
        "date_of_birth": "2000-01-01",
        "email": "temp@test.edu",
        "phone": "+1-555-6001"
    }
    client.post("/students", json=payload)

    # Delete the student
    del_res = client.delete("/students/STU-6001")
    assert del_res.status_code == 200
    assert "successfully deleted" in del_res.json()["message"]

    # Verify student is no longer in database
    get_res = client.get("/students/STU-6001")
    assert get_res.status_code == 404

    # Second delete returns 404
    del_res2 = client.delete("/students/STU-6001")
    assert del_res2.status_code == 404


def test_ask_ai_offline_handling():
    """
    Test that calling the AI endpoint when Ollama is offline returns HTTP 503
    with a clear, user-friendly instruction message.
    """
    # Create at least one student so context is present
    payload = {
        "student_id": "STU-7001",
        "name": "Grace Hopper",
        "date_of_birth": "1906-12-09",
        "email": "grace@navy.mil",
        "phone": "+1-555-7001",
        "course": "Computer Science"
    }
    client.post("/students", json=payload)

    response = client.post("/students/ask", json={"question": "Who is studying Computer Science?"})
    # If Ollama is offline (standard dev environment), expect 503 Service Unavailable
    assert response.status_code in [200, 503]
    if response.status_code == 503:
        assert "Could not connect to Ollama" in response.json()["detail"]

