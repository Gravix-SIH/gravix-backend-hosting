# Project Structure -- MindMate Chatbot

This document describes the repository layout for the **MindMate mental
health chatbot** project.

------------------------------------------------------------------------

## Root Directory

    mindmate/
    ├── backend/                     # Django backend
    ├── docs/                        # Documentation
    ├── scripts/                     # Utility scripts
    ├── tests/                       # Automated tests
    ├── .gitignore
    ├── README.md
    └── LICENSE

------------------------------------------------------------------------

## Backend

The backend is built with **Django** and contains all apps, APIs, and
business logic.

    backend/
    ├── manage.py                    # Django management script
    ├── requirements.txt             # Backend dependencies
    ├── mindmate/                    # Project configuration (settings, urls, wsgi)
    │   ├── __init__.py
    │   ├── settings.py
    │   ├── urls.py
    │   └── wsgi.py
    │
    ├── apps/                        # Django apps (modular)
    │   ├── chat/                    # Chat-related logic
    │   │   ├── models.py            # Chat history model
    │   │   ├── views.py             # Chat API endpoints
    │   │   ├── urls.py
    │   │   └── serializers.py
    │   │
    │   ├── assessments/             # Mental health screenings (PHQ-9, GAD-7)
    │   │   ├── models.py            # Store results
    │   │   ├── views.py             # API for assessments
    │   │   ├── urls.py
    │   │   └── forms.py             # Assessment forms
    │   │
    │   ├── booking/                 # Counselor booking system
    │   │   ├── models.py
    │   │   ├── views.py
    │   │   ├── urls.py
    │   │   └── serializers.py
    │   │
    │   └── resources/               # Self-help resources and exercises
    │       ├── models.py
    │       ├── views.py
    │       ├── urls.py
    │       └── serializers.py
    │
    └── db.sqlite3                   # Development database (use PostgreSQL in prod)

------------------------------------------------------------------------

## Docs

All documentation related to chatbot behavior, APIs, and architecture.

    docs/
    ├── claude.md                    # Claude instructions (chatbot behavior)
    ├── project-structure.md         # Current document
    ├── architecture.md              # High-level system design
    └── api-spec.md                  # API contracts (endpoints, payloads, responses)

------------------------------------------------------------------------

## Scripts

Utility scripts for development or deployment.

    scripts/
    └── seed_data.py                 # Preload resources, assessments, or counselor data

------------------------------------------------------------------------

## Tests

Backend tests for each module.

    tests/
    ├── chat_tests.py
    ├── assessment_tests.py
    ├── booking_tests.py
    └── resource_tests.py

------------------------------------------------------------------------

## Notes

-   **Secrets** (like API keys) must be stored in environment variables
    (`.env` for local dev).\
-   **No frontend is included** in this repo --- focus is entirely
    backend + docs.\
-   Django apps are **modular** and can be extended (e.g., adding RAG to
    `resources/` later).
