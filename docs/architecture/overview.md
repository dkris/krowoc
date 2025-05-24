# Krowoc Architecture Overview

This document provides an overview of the Krowoc architecture, including design decisions, component interactions, and implementation details.

## System Architecture

Krowoc follows a modern, modular architecture with separate backend and frontend services:

```
                     ┌───────────────┐
                     │   Frontend    │
                     │   (Next.js)   │
                     └───────┬───────┘
                             │
                             ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│  Orchestration │◄───┤    Backend    │◄───┤    Database   │
│    (Prefect)   │    │    (Flask)    │    │   (Postgres)  │
└───────────────┘    └───────┬───────┘    └───────────────┘
                             │
                             ▼
                     ┌───────────────┐
                     │      LLM      │
                     │   Providers   │
                     └───────────────┘
```

### Key Components

1. **Frontend (Next.js)**
   - User interface for managing prompts and viewing results
   - Built with Next.js, React, TypeScript, and Tailwind CSS
   - Communicates with backend via GraphQL API

2. **Backend (Flask)**
   - Core business logic and API endpoints
   - Handles authentication, data validation, and LLM integration
   - Built with Flask, SQLAlchemy, and GraphQL

3. **Database (PostgreSQL)**
   - Unified data store for users, prompts, executions, etc.
   - Uses SQLAlchemy ORM for database interaction
   - Alembic for database migrations

4. **Orchestration (Prefect)**
   - Manages workflow execution for complex prompt chains
   - Handles background jobs and scheduled tasks
   - Provides reliability and retries for LLM operations

5. **Caching and Messaging (Redis)**
   - Handles session management and caching
   - Provides pub/sub for real-time updates
   - Supports rate limiting and job queues

### Data Flow

1. User submits a prompt through the frontend
2. Request is validated and processed by the backend
3. Backend initiates a workflow in the orchestration service
4. Orchestration executes the prompt against LLM providers
5. Results are stored in the database and returned to the frontend
6. Analytics and metrics are updated

## Design Decisions

### Authentication

- Using Supabase Auth with OAuth2 and PKCE for secure authentication
- HTTP-only cookies with CSRF protection for token storage
- JWT-based authentication with short lifetimes and refresh tokens

### Database Schema

- Unified Postgres database for all data storage
- Clearly defined relationships between models:
  - User -> Prompts (one-to-many)
  - User -> API Keys (one-to-many)
  - Prompt -> Executions (one-to-many)

### API Design

- GraphQL for flexible, strongly-typed API contracts
- Schema-first approach with code generation
- Pydantic models for validation and documentation

### LLM Integration

- Using LangChain for a unified interface to multiple LLM providers
- Supports advanced features such as prompt templates, chains, memory, and agents
- Streaming and synchronous prompt execution via LangChain's APIs
- Prompt versioning for reproducibility

### Error Handling

- Comprehensive error handling with structured logging
- Retry strategies for transient failures
- DLQ (Dead Letter Queue) for failed executions

## Security Considerations

- API keys are stored securely with hashing (e.g., `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GOOGLE_API_KEY`)
- All endpoints require authentication
- CSRF protection for all state-changing operations
- Rate limiting to prevent abuse

## Performance Optimization

- Caching strategy for frequent operations
- Connection pooling for database access
- Edge caching for static assets
- Database indexing for common query patterns

## Monitoring and Observability

- PostHog for analytics and error tracking
- Structured logging with correlation IDs
- Health check endpoints for service monitoring
- Performance metrics tracking 