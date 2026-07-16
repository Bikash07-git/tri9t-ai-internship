\# Tri9T AI Engineering Internship - Backend Pipeline



This repository contains the backend API and document parsing pipeline for the CardioTrack CT-200 assignment.



\## Tech Stack

\* \*\*Framework:\*\* FastAPI

\* \*\*Database:\*\* SQLite + SQLAlchemy

\* \*\*Document Parsing:\*\* PyMuPDF (fitz)

\* \*\*LLM Storage:\*\* Local JSON Store (`test\_cases\_store.json`)



\## Setup Instructions

1\. \*\*Create and activate a virtual environment:\*\*

&#x20;  `python -m venv venv`

&#x20;  \* Windows: `venv\\Scripts\\activate`

&#x20;  \* Mac/Linux: `source venv/bin/activate`

2\. \*\*Install dependencies:\*\*

&#x20;  `pip install fastapi uvicorn sqlalchemy pymupdf pydantic`

3\. \*\*Start the API Server:\*\*

&#x20;  `uvicorn main:app --reload`

4\. Access the interactive API docs at: `http://127.0.0.1:8000/docs`



\## Triggering the v1 → v2 Re-ingestion Flow

To demonstrate the versioning and staleness detection, follow these steps:



1\. \*\*Ingest Version 1:\*\* Run `python parser.py` (ensure the script is pointing to `ct200\_manual.pdf` and version "v1").

2\. \*\*Create a Selection \& Generate Tests:\*\* Using the Swagger UI at `/docs`, create a selection via `POST /selections/` and generate test cases via `POST /generate/{selection\_id}`.

3\. \*\*Ingest Version 2:\*\* Update `parser.py` to point to `ct200\_manual\_v2.pdf` and version "v2", then run `python parser.py` again.

4\. \*\*Test Staleness:\*\* Run the `GET /retrieval/{selection\_id}` endpoint. Sections where the text changed (like Section 3.2) will dynamically report `"is\_stale": true`.

