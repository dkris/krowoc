# Krowoc Backend

This directory contains the Flask backend API and business logic for Krowoc.

## Technology Stack

- Flask (Python)
- SQLAlchemy ORM for database interaction
- Alembic for database migrations
- GraphQL for API contracts
- Pydantic for data validation
- langchain for LLM integration
- loguru for structured logging
- Pytest for testing

## Getting Started

Coming soon...

## Development

```bash
# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the development server
flask run
```

## Directory Structure

```
backend/
├── api/             # API endpoints and routes
├── models/          # Database models and schemas
├── services/        # Business logic and services
├── migrations/      # Alembic database migrations
├── tests/           # Unit and integration tests
└── utils/           # Utility functions and helpers
``` 