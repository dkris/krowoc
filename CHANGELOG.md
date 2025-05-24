# Changelog

All notable changes to the Krowoc project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2024-XX-XX

### Changed
- Major framework migration: replaced all LLM integration from aisuite to LangChain.
- Updated backend LLM service to use LangChain's model wrappers and chain abstractions.
- Updated all environment variables and documentation for LangChain.
- All prompt execution, streaming, and advanced LLM features now powered by LangChain.

### Removed
- All aisuite dependencies, code, and documentation.
- All aisuite-related environment variables.

### Added
- LangChain integration: unified support for OpenAI, Anthropic, Google Gemini, and other providers via LangChain.
- Support for advanced prompt templates, chains, memory, and agent workflows.
- Updated documentation and setup guides for LangChain.

## [Unreleased]

### Added

#### Analytics & Observability
- Implemented comprehensive PostHog analytics integration:
  - Created frontend analytics module with event tracking utilities
  - Added backend PostHog integration for server-side events
  - Implemented correlation ID system for cross-service tracking
  - Added standardized event tracking for key user actions
  - Created middleware for correlation ID propagation
  - Added error tracking with context preservation
  - Integrated with API requests for automatic tracking
  - Implemented automatic request/response logging with correlation IDs
  - Added comprehensive test suite for correlation ID flow
  - Created detailed analytics documentation

#### Frontend (Next.js)
- Implemented comprehensive user dashboard:
  - Created dashboard page with usage metrics overview
  - Added visualization components for data presentation
  - Implemented time range selection for daily metrics
  - Added support for mock data through URL flags
  - Created responsive layout for desktop and mobile views
- Enhanced API client with correlation ID support:
  - Created centralized API client with consistent error handling
  - Added automatic correlation ID generation and propagation
  - Implemented standard event tracking for all API requests
  - Added robust error handling with error event tracking

#### Backend (Flask)
- Created usage metrics API:
  - Implemented `/api/metrics/summary` endpoint for overall usage metrics
  - Added `/api/metrics/daily` endpoint for daily usage data
  - Created `/api/metrics/cost_breakdown` endpoint for provider cost analysis
  - Implemented authentication middleware for secure access
  - Added database utilities for querying execution data
- Enhanced logging system:
  - Implemented structured logging with consistent correlation IDs
  - Added improved error handling with automatic tracking
  - Created middleware for request/response logging
  - Added environment-specific logging configuration

#### User Settings
- Implemented comprehensive user settings management:
  - Created settings page with tabbed interface for organization
  - Added user profile settings for updating personal information
  - Added preferences section for application preferences (theme, notifications)
  - Integrated settings into the main navigation
- Implemented provider API key management:
  - Created secure storage for third-party API keys (OpenAI, Anthropic, Google)
  - Added UI for adding, testing, and deleting provider keys
  - Implemented backend API endpoints for provider key operations
  - Created utility functions for secure key retrieval and validation
  - Added key verification endpoint for testing provider connections
  - Set up key usage tracking with last-used timestamps
- Enhanced security measures:
  - Implemented key hashing for secure storage
  - Added row-level security policies for user data
  - Created user-specific database constraints
  - Limited exposed key information to prefixes only

## [1.2.0] - 2024-08-02

### Added

#### Backend (Flask)
- Implemented comprehensive Redis integration:
  - Created modular Redis client utility with singleton pattern
  - Added function-level caching with customizable TTLs
  - Implemented cache invalidation by pattern matching
  - Developed Redis Pub/Sub for event-based communication
  - Added rate limiting for API protection with customizable limits
  - Created example API endpoints demonstrating Redis features
  - Added health check integration for Redis monitoring
  - Created detailed documentation for Redis features

#### LLM Integration
- Implemented `aisuite` library integration for unified LLM access
- Created LLM service with comprehensive provider/model support:
  - Added support for OpenAI, Anthropic, and Google models
  - Implemented model validation and whitelisting
  - Created utility functions for provider/model management
- Added new prompt execution endpoints:
  - `/api/prompts/execute` for executing arbitrary prompts
  - `/api/prompts/<id>/execute` for executing stored prompts
- Implemented streaming response handling with Server-Sent Events (SSE)
- Added support for system prompts and tools
- Created comprehensive documentation for LLM integration
- Updated environment configuration with necessary API keys

#### Frontend (Next.js)
- Implemented complete prompt management UI:
  - Created PromptEditor component for creating and editing prompts
  - Built PromptCard component to display prompt information
  - Implemented PromptList component to display a grid of prompt cards
  - Added prompt management pages:
    - /prompts - Main listing page for user's prompts
    - /prompts/new - Page for creating a new prompt
    - /prompts/[id] - Page for viewing a specific prompt
    - /prompts/edit/[id] - Page for editing an existing prompt
  - Created TypeScript types for prompts
  - Implemented prompt API client with Supabase
  - Updated Layout component with navigation for prompts
  - Added proper error handling and loading states
  - Implemented authentication checks for protected routes

#### Backend (Flask)
- Implemented GraphQL API with Graphene:
  - Created type definitions for Users, Prompts, Executions, and API Keys
  - Implemented comprehensive queries with filtering and pagination
  - Added mutations for CRUD operations on all entities
  - Set up validation using Pydantic for all inputs
  - Added secure API key storage with hashing
  - Created GraphQL endpoint with GraphiQL interface
  - Implemented proper error handling and validation

## [1.1.0]

### Added

#### Frontend (Next.js)
- Configured Tailwind CSS with proper configuration files
- Set up PostCSS for processing Tailwind directives
- Added global CSS styles with Tailwind imports
- Created modular layout component system:
  - Implemented base Layout component with responsive design
  - Added header, main content area, and footer sections
  - Configured proper meta tags and viewport settings
- Updated application structure to use layout components
- Improved project documentation with detailed README
- Implemented Supabase authentication foundation:
  - Created auth client configuration and utility functions
  - Built React context for managing authentication state
  - Added customizable form hooks with validation
  - Implemented email/password authentication
  - Added OAuth provider support (Google, GitHub, Microsoft)
  - Created authentication UI components and pages
  - Added protected routes with client and server-side validation
  - Implemented middleware for session handling
  - Created user profile page for authenticated users
  - Added comprehensive documentation for auth setup

#### Backend (Flask)
- Created database initialization and migration scripts for automated setup:
  - Added init_db.py script that waits for database availability and runs migrations
  - Created entrypoint.sh to execute initialization before application startup
  - Ensured initial schema migration will be created automatically if none exists
  - Added robust retry mechanism for database connection
  - Implemented proper error handling for migration failures
- Updated Docker configuration to run migrations on startup
- Integrated database health check into application startup sequence

#### Development Environment
- Enhanced PostgreSQL integration with automated database initialization
- Streamlined developer experience with zero-setup database configuration

### Fixed

#### Frontend
- Fixed CSS loading on the start page by:
  - Added proper Tailwind CSS configuration with tailwind.config.js
  - Created _app.tsx file to import global styles
  - Added globals.css with Tailwind directives
  - Configured PostCSS with postcss.config.js

## [1.0.0]

### Added

#### Project Structure
- Initialized repository structure with frontend, backend, orchestration, and docs directories
- Created README.md with project overview and structure
- Added .gitignore for Python, Node.js, and other related tools
- Created directory-specific README files with documentation
- Added docker-compose.yml for local development environment
- Created Dockerfile.dev files for each service
- Implemented Git branching strategy based on GitFlow

#### Backend (Flask)
- Set up Flask application structure with app.py entry point
- Configured SQLAlchemy ORM with database models:
  - User model for authentication and user data
  - Prompt model for storing prompt data
  - ApiKey model for secure storage of provider keys
  - Execution model for tracking prompt executions
- Implemented Alembic for database migrations
- Added requirements.txt with dependencies
- Added comprehensive health check endpoints:
  - Basic health check at `/health`
  - Detailed system information at `/health/detailed`
  - Deep connectivity checks at `/health/deep`
- Configured structured logging with loguru:
  - Request correlation IDs for request tracking
  - JSON formatting for production logs
  - Automatic log rotation and retention
  - Environment-configurable log levels
- Implemented modular API architecture with blueprints
- Added middleware for request logging and context propagation
- Created standardized error handling for API responses
- Added pytest configuration and initial health check tests

#### Frontend (Next.js)
- Created basic Next.js application with TypeScript
- Set up package.json with dependencies
- Created initial home page with links to main sections
- Configured TypeScript with tsconfig.json

#### Orchestration (Prefect)
- Set up basic Prefect workflow structure
- Created sample prompt execution flow
- Added requirements.txt with dependencies

#### Development Environment
- Added environment variable example file (_env.example)
- Configured Docker for local development

