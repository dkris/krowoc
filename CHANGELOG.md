# Changelog

All notable changes to the Krowoc project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

