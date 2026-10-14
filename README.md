# Student Records Management System 🎓

> **Backend Development Project 01**  
> A high-performance, modular RESTful API for managing student records using **FastAPI**, **SQLite**, and **SQLAlchemy**, featuring an optional **Ollama LLM Extension** to query student records using natural language.

---

## 📌 01. Project Objectives & Overview

The objective of this project is to build a reliable backend service implementing full **CRUD** (Create, Read, Update, Delete) operations for managing student educational and contact profiles. 

### Key Highlights
- **FastAPI Framework:** Fast, modern Python web framework featuring automatic interactive API docs (Swagger UI & ReDoc).
- **SQLite & SQLAlchemy ORM:** Persistent, lightweight relational storage with declarative ORM models and automated schema creation.
- **Strict Data Validation:** Robust data validation and formatting using Pydantic v2 schemas (email validation, regex checks for dates).
- **Optional Ollama AI Extension:** Natural language interface querying stored student records using local open-source LLMs (such as LLaMA 3, Mistral, or Phi-3) via Ollama.
- **Automated Testing:** 100% test coverage for all endpoints and failure scenarios with `pytest` and an isolated in-memory SQLite database.

---

## 🏗️ 02. Project Architecture & Directory Structure

The project follows a clean, decoupled MVC/service pattern standard in modern Python development:

```
student-management-system/
│
├── app/
│   ├── __init__.py           # Package marker
│   ├── database.py           # SQLite engine, sessionmaker, and DB dependency (get_db)
│   ├── models.py             # SQLAlchemy ORM models (Student table mapping)
│   ├── schemas.py            # Pydantic v2 request/response validation schemas
│   ├── crud.py               # Data access layer (Create, Read, Update, Delete functions)
│   ├── ai_service.py         # Ollama LLM integration for natural language questions
│   └── main.py               # FastAPI application, route handlers, and lifecycle hooks
│
├── seed_data.py              # Script to populate SQLite with sample student records
├── test_main.py              # Pytest test suite (10 automated unit & integration tests)
├── requirements.txt          # Production and testing dependencies
├── .env.example              # Template for environment configuration
├── .gitignore                # Git exclusions (virtualenvs, .db files, cache)
└── README.md                 # Complete project documentation & guide
```

---

## 📋 03. Student Record Fields

Each student record is stored in SQLite with the following attributes:

| Field Name | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | Integer | Primary Key, Auto-increment | Internal unique database record ID |
| `student_id` | String | Unique, Indexed, Required | Unique Student ID code (e.g. `STU-1001`) |
| `name` | String | Required | Full student name (e.g. `Alice Johnson`) |
| `date_of_birth` | String | Required (YYYY-MM-DD) | Date of birth (e.g. `2003-05-14`) |
| `email` | String | Unique, Indexed, Required | Valid student email address |
| `phone` | String | Required | Phone number (e.g. `+1-555-0101`) |
| `course` | String | Optional, Indexed | Program/Major (e.g. `Computer Science`) |
| `address` | String | Optional | Residential or campus address |
| `enrollment_date` | String | Optional (YYYY-MM-DD) | Date of admission (defaults to current date) |
| `created_at` | DateTime | Auto-generated (UTC) | Timestamp when the record was created |

---

## 🚀 04. Getting Started & Setup

### Prerequisites
- Python 3.10+ (tested on Python 3.14)
- (Optional) [Ollama](https://ollama.com/) installed if using natural-language AI queries

### Step 1: Clone or Open the Project
Navigate to the project root directory:
```bash
cd student-management-system
```

### Step 2: Activate the Virtual Environment
If using Windows PowerShell:
```powershell
.\.venv\Scripts\Activate.ps1
```
*(Or on Linux/macOS: `source .venv/bin/activate`)*

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Seed Sample Data (Optional but Recommended)
Populate the SQLite database with 6 realistic student profiles across different majors:
```bash
python seed_data.py
```

### Step 5: Start the FastAPI Server
Run the application with Uvicorn live-reloading:
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The server will be running at `http://127.0.0.1:8000`.

---

## 📖 05. Interactive API Documentation

FastAPI automatically generates interactive documentation:
- **Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) (Test endpoints directly in your browser)
- **ReDoc:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc) (Clean, structured reference documentation)

---

## 🔌 06. API Endpoints Specification

| Method | Endpoint | Description | Status Code |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | API Health Check and endpoint index | 200 OK |
| `POST` | `/students` | Register a new student record | 201 Created |
| `GET` | `/students` | List all students with search & course filtering | 200 OK |
| `GET` | `/students/{student_id}` | Retrieve details of a specific student | 200 OK / 404 |
| `PUT` | `/students/{student_id}` | Full update of an existing student's details | 200 OK / 404 / 400 |
| `PATCH`| `/students/{student_id}` | Partial update of specific fields | 200 OK / 404 / 400 |
| `DELETE`| `/students/{student_id}` | Remove a student record from the database | 200 OK / 404 |
| `POST` | `/students/ask` | Natural language Q&A about student records (Ollama) | 200 OK / 503 |

---

## 💻 07. Example API Requests & Responses

### 1. Create a Student (`POST /students`)
**Request:**
```bash
curl -X POST "http://127.0.0.1:8000/students" \
     -H "Content-Type: application/json" \
     -d '{
       "student_id": "STU-1007",
       "name": "Grace Hopper",
       "date_of_birth": "2003-12-09",
       "email": "grace.hopper@campus.edu",
       "phone": "+1-555-0107",
       "course": "Computer Science",
       "address": "42 Naval Yard Ave, Cityville",
       "enrollment_date": "2024-09-01"
     }'
```
**Response (201 Created):**
```json
{
  "student_id": "STU-1007",
  "name": "Grace Hopper",
  "date_of_birth": "2003-12-09",
  "email": "grace.hopper@campus.edu",
  "phone": "+1-555-0107",
  "course": "Computer Science",
  "address": "42 Naval Yard Ave, Cityville",
  "enrollment_date": "2024-09-01",
  "id": 7,
  "created_at": "2026-10-14T11:20:00Z"
}
```

---

### 2. List & Filter Students (`GET /students`)
- **List All:** `GET http://127.0.0.1:8000/students`
- **Filter by Course:** `GET http://127.0.0.1:8000/students?course=Computer%20Science`
- **Search by Name/ID:** `GET http://127.0.0.1:8000/students?search=Alice`
- **Pagination:** `GET http://127.0.0.1:8000/students?skip=0&limit=10`

---

### 3. View a Student (`GET /students/{student_id}`)
```bash
curl -X GET "http://127.0.0.1:8000/students/STU-1001"
```
*(You can also query by internal integer ID: `GET http://127.0.0.1:8000/students/1`)*

---

### 4. Update Student Details (`PATCH /students/{student_id}`)
```bash
curl -X PATCH "http://127.0.0.1:8000/students/STU-1001" \
     -H "Content-Type: application/json" \
     -d '{
       "phone": "+1-555-9999",
       "course": "Advanced Artificial Intelligence"
     }'
```

---

### 5. Delete a Student (`DELETE /students/{student_id}`)
```bash
curl -X DELETE "http://127.0.0.1:8000/students/STU-1007"
```
**Response (200 OK):**
```json
{
  "message": "Student record 'STU-1007' (Grace Hopper) was successfully deleted.",
  "detail": null
}
```

---

## 🤖 08. Optional Ollama AI Extension

The API includes a dedicated endpoint (`POST /students/ask`) that allows users to ask freeform natural language questions about the student records.

### How it works:
1. When a user asks a question, the API retrieves the stored student records from SQLite.
2. The records are serialized into structured JSON and sent along with a context-constrained prompt to your local Ollama LLM.
3. The LLM analyzes the data and replies accurately without hallucinating outside facts.
4. If Ollama is offline or uninstalled, the API gracefully returns HTTP 503 with instructions on how to start it.

### Setup Ollama:
1. Download and install Ollama from [ollama.com](https://ollama.com/).
2. Pull a model (e.g. `llama3` or `phi3`):
   ```bash
   ollama pull llama3
   ```
3. Ensure Ollama service is running:
   ```bash
   ollama serve
   ```

### Example Natural Language Query:
**Request:**
```bash
curl -X POST "http://127.0.0.1:8000/students/ask" \
     -H "Content-Type: application/json" \
     -d '{
       "question": "How many students are enrolled in Computer Science, and what are their names?",
       "model": "llama3"
     }'
```

**Response (200 OK):**
```json
{
  "question": "How many students are enrolled in Computer Science, and what are their names?",
  "answer": "There are 2 students enrolled in Computer Science:\n1. Alice Johnson (STU-1001)\n2. Clara Chen (STU-1003)",
  "students_in_context": 6,
  "model_used": "llama3"
}
```

---

## 🧪 09. Running Automated Tests

A comprehensive Pytest suite is provided in `test_main.py`. The tests use an **in-memory SQLite database** with dependency injection overrides, guaranteeing that your real `students.db` data is never modified by testing.

To run the test suite:
```bash
pytest -v
```

### Test Coverage Checklist:
- [x] API root endpoint & status check
- [x] Successful student creation
- [x] Duplicate `student_id` validation rejection (HTTP 400)
- [x] Duplicate `email` validation rejection (HTTP 400)
- [x] Malformed email format validation (HTTP 422)
- [x] Student listing and course/search filtering
- [x] View individual student by ID and 404 check
- [x] Full (PUT) and Partial (PATCH) student updates
- [x] Deletion of student records and verification of removal
- [x] Graceful AI service degradation when Ollama is offline (HTTP 503)

---

## 🎓 10. Design Decisions & Best Practices

1. **Separation of Concerns:** 
   - `models.py` handles database table schemas.
   - `schemas.py` handles validation and serialization.
   - `crud.py` isolates SQL operations.
   - `main.py` focuses purely on routing and HTTP status codes.
2. **Defensive Validation:** 
   Emails and dates are validated both at the Pydantic schema boundary and with uniqueness checks in the database layer.
3. **Idempotent Data Seeding:** 
   `seed_data.py` checks for existing records before inserting, making it safe to run multiple times.
4. **Graceful Fallbacks:** 
   Ollama AI queries handle timeouts, missing models, and connection errors with helpful troubleshooting hints.
