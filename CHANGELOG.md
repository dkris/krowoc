# Changelog

All notable changes to the Krowoc project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

## [1.0.0] - 2024-07-21

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