"""
ai_service.py
-------------
Optional Ollama extension service for answering natural language questions
about the student records stored in SQLite.
"""

import json
import os
from typing import List
import httpx
from fastapi import HTTPException, status

from app import models

# Default Ollama configuration
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "llama3")


def format_student_records(students: List[models.Student]) -> str:
    """Format the student database rows into clean JSON for the LLM context."""
    records = []
    for s in students:
        records.append({
            "student_id": s.student_id,
            "name": s.name,
            "date_of_birth": s.date_of_birth,
            "email": s.email,
            "phone": s.phone,
            "course": s.course or "Not specified",
            "address": s.address or "Not specified",
            "enrollment_date": s.enrollment_date or "Not specified"
        })
    return json.dumps(records, indent=2)


async def ask_ollama(question: str, students: List[models.Student], model_name: str = DEFAULT_MODEL) -> str:
    """
    Sends a query along with the student records database context to the local Ollama instance.
    
    Parameters:
        question: Natural language question from user
        students: Current list of students from the database
        model_name: Name of the Ollama model (e.g. 'llama3', 'mistral', 'phi3')
        
    Returns:
        The generated answer string from the LLM.
    """
    if not students:
        return "The student database is currently empty. Please add some student records first."

    context_json = format_student_records(students)

    system_prompt = (
        "You are an intelligent school database assistant. You have direct access to "
        "the current student records database in JSON format below.\n"
        "Your job is to answer questions about these students accurately, concisely, and politely.\n"
        "Do not invent facts not present in the records."
    )

    user_prompt = f"""Student Database Records:
```json
{context_json}
```

Question:
{question}

Please answer the question based only on the student records provided above."""

    payload = {
        "model": model_name,
        "prompt": f"{system_prompt}\n\n{user_prompt}",
        "stream": False,
        "options": {
            "temperature": 0.2
        }
    }

    url = f"{OLLAMA_BASE_URL}/api/generate"

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, json=payload)
            
            if response.status_code == 404:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=(
                        f"Ollama model '{model_name}' was not found. "
                        f"Run 'ollama pull {model_name}' in your terminal to download it."
                    )
                )

            response.raise_for_status()
            data = response.json()
            return data.get("response", "").strip()

    except httpx.ConnectError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                f"Could not connect to Ollama at {OLLAMA_BASE_URL}. "
                "Please make sure Ollama is installed and running (e.g., run 'ollama serve' in terminal)."
            )
        )
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=f"The Ollama model '{model_name}' took too long to respond. Try again or use a lighter model."
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to query Ollama: {str(e)}"
        )
