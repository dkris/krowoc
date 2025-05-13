# Krowoc Backend

This directory contains the Flask backend API and business logic for Krowoc.

## Technology Stack

- Flask (Python)
- SQLAlchemy ORM for database interaction
- Alembic for database migrations
- GraphQL for API contracts
- Pydantic for data validation
- aisuite for LLM integration
- Supabase for authentication
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

# Set up environment variables
cp ../_env.example .env
# Edit .env with your Supabase credentials

# Run the development server
flask run
```

## Authentication

Authentication is implemented using Supabase Auth with JWT validation:

1. Users authenticate with Supabase on the frontend
2. JWT tokens are passed to the backend via Authorization header
3. Backend validates the token using the Supabase JWT secret
4. User is created in our database if they don't exist

Protected routes can be secured using the `@login_required` decorator.

## Directory Structure

```
backend/
├── api/             # API endpoints and routes
├── models/          # Database models and schemas
├── services/        # Business logic and services
├── middleware/      # Middleware components (auth, logging, etc.)
├── migrations/      # Alembic database migrations
├── tests/           # Unit and integration tests
└── utils/           # Utility functions and helpers
``` 