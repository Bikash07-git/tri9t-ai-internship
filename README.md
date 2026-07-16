# Tri9T AI Internship Assignment

## Overview

This project implements an AI-assisted backend system for managing versioned technical manuals.

The application parses PDF manuals, extracts hierarchical document structures, stores them in a SQLite database, generates LLM-based test cases, and detects whether previously generated test cases become stale after a newer version of the document is uploaded.

The backend is developed using FastAPI and demonstrates document parsing, version management, retrieval, and automated staleness detection.

---

## Features

- Parse PDF manuals using PyMuPDF
- Extract document hierarchy
- Store document versions in SQLite
- Generate structured test cases
- Retrieve saved test cases
- Compare document versions
- Detect stale test cases after document updates
- RESTful API with Swagger UI

---

## Tech Stack

- Python 3.13
- FastAPI
- SQLite
- SQLAlchemy
- PyMuPDF (fitz)
- Pydantic
- Uvicorn

---

## Project Structure

```
tri9t_assignment/
│
├── data/
│   ├── ct200_manual.pdf
│   └── ct200_manual_v2.pdf
│
├── database.py
├── models.py
├── parser.py
├── schemas.py
├── main.py
├── requirements.txt
├── README.md
└── .gitignore
```

---

## Installation

Clone the repository

```bash
git clone https://github.com/Bikash07-git/tri9t-ai-internship.git
```

Move into the project

```bash
cd tri9t-ai-internship
```

Create a virtual environment

```bash
python -m venv venv
```

Activate it

Windows

```bash
venv\Scripts\activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

## Run the Application

Start the FastAPI server

```bash
uvicorn main:app --reload
```

Application

```
http://127.0.0.1:8000
```

Swagger Documentation

```
http://127.0.0.1:8000/docs
```

---

## API Endpoints

### Upload / Parse Document

Parses and stores a document version.

### Retrieve Test Cases

```
GET /retrieval/{selection_id}
```

Returns

- Generated test cases
- Version information
- Staleness status
- Node comparison details

---

## Version Comparison

The application compares multiple document versions using content hashes.

If a document section changes in a newer version:

- The section is marked as updated.
- Existing test cases become stale.
- The API reports the affected nodes.

---

## Database

SQLite is used to store

- Documents
- Document versions
- Hierarchical nodes
- User selections
- Generated test cases

---

## Assumptions

- PDFs follow a structured technical documentation format.
- Headings can be identified using formatting and hierarchy.
- Documents are uploaded sequentially as new versions.
- Generated test cases are associated with document nodes.

---

## Future Improvements

- OCR support for scanned PDFs
- Vector database integration
- Semantic similarity matching
- OpenAI/Gemini based test generation
- Authentication and user management
- Docker deployment
- PostgreSQL support

---

## Author

**Bikash Sagar Koiri**

GitHub:
https://github.com/Bikash07-git
