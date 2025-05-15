# Krowoc

Krowoc is a platform for managing and executing prompts across multiple LLM providers.

## Overview

- User-friendly web application for creating, organizing, and executing prompts
- Integration with multiple LLM providers (OpenAI, Anthropic Claude, Google Gemini) via the `aisuite` library
- Bring your own API keys for LLM providers
- Dashboard with key usage metrics
- Browser extension for easy prompt capture
- Robust and scalable architecture

## Features

### Prompt Management
- Create, edit, and organize prompts with tags and descriptions
- Version control for prompts
- Access controls and sharing options

### LLM Integration
- Execute prompts with any supported LLM model
- Model whitelisting for specific prompts
- Streaming responses for real-time interactions
- Support for system prompts and tool calling
- Provider-agnostic API through `aisuite`

## Technology Stack

- **Frontend:** NextJS (React + TypeScript), Tailwind CSS, VisActor
- **Backend:** Flask (Python), Prefect for orchestration
- **Database:** Postgres (unified data store)
- **Messaging & Caching:** Redis
- **LLM Integration:** [`aisuite`](https://github.com/andrewyng/aisuite)
- **Observability:** PostHog, Python `loguru` for logging

## Project Structure

```
krowoc/
├── frontend/         # NextJS frontend application
├── backend/          # Flask backend API and business logic
├── orchestration/    # Prefect workflow definitions
└── docs/             # Project documentation
```

## Development Setup

For detailed setup instructions, see [Getting Started Guide](docs/development/getting-started.md).

### LLM API Keys
To use the LLM integration features, you'll need to set up API keys for your chosen providers:
1. Copy `_env.example` to `.env`
2. Add your API keys for supported providers

## API Endpoints

### LLM Execution
- `POST /api/prompts/execute` - Execute an arbitrary prompt with any supported model
- `POST /api/prompts/<id>/execute` - Execute a stored prompt with specified parameters
- Both endpoints support streaming responses using Server-Sent Events

## Git Workflow

This project follows a GitFlow-inspired branching strategy:

- `main` - Production-ready code
- `develop` - Integration branch for active development
- Feature branches (`feature/*`) - For new features
- Bugfix branches (`bugfix/*`) - For non-critical bug fixes
- Hotfix branches (`hotfix/*`) - For critical production fixes

For complete details, see our [Git Branching Strategy](docs/GIT_BRANCHING_STRATEGY.md).

## Documentation

- [Project Status](PROJECT_STATUS.md) - Current status and next steps
- [Changelog](CHANGELOG.md) - History of changes and releases
- [Development Docs](docs/development/) - Development guides and documentation
- [Architecture Overview](docs/architecture/overview.md) - System architecture and design decisions

## Contributing

Please read our [Contributing Guidelines](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

Coming soon... 