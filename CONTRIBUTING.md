# Contributing to Krowoc

Thank you for your interest in contributing to Krowoc! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

Please be respectful and considerate in all interactions within this project's community. We strive to create a welcoming and inclusive environment for everyone.

## Getting Started

1. Fork the repository
2. Clone your fork locally: `git clone <your-fork-url>`
3. Set up your development environment (see [Getting Started Guide](docs/development/getting-started.md))
4. Create a new branch for your contribution: `git checkout -b feature/your-feature-name`

## Development Workflow

1. Make your changes in your feature branch
2. Write or update tests as needed
3. Ensure all tests pass: 
   - Backend: `cd backend && pytest`
   - Frontend: `cd frontend && npm test`
4. Follow the code style guidelines
5. Commit your changes with clear, descriptive messages using [Conventional Commits](https://www.conventionalcommits.org/)
6. Push to your fork
7. Submit a pull request

## Pull Request Guidelines

- Fill in the pull request template completely
- Link any related issues
- Include screenshots or GIFs for UI changes
- Update documentation if necessary
- Ensure all CI checks pass
- Request code review from appropriate maintainers

## Commit Message Guidelines

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification for commit messages:

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

Types include:
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `style`: Changes that do not affect the meaning of the code
- `refactor`: A code change that neither fixes a bug nor adds a feature
- `perf`: A code change that improves performance
- `test`: Adding missing tests or correcting existing tests
- `chore`: Changes to the build process or auxiliary tools

Example:
```
feat(prompt): add prompt versioning functionality

Implement version history tracking for prompts, allowing users to revert to previous versions.

Closes #123
```

## Code Style Guidelines

### Python (Backend)
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide
- Use [Black](https://github.com/psf/black) for formatting
- Sort imports with [isort](https://pycqa.github.io/isort/)
- Use type hints

### TypeScript/JavaScript (Frontend)
- Follow ESLint and Prettier configuration
- Use TypeScript interfaces for type definitions
- Follow React best practices and hooks

## Testing Guidelines

- Write unit tests for all new functionality
- Maintain or improve code coverage
- Include both happy path and error cases
- Mock external dependencies

## Documentation Guidelines

- Keep README and other documentation up to date
- Document all public APIs, components, and functions
- Use clear, concise language
- Include examples where appropriate

## Issue Guidelines

### Reporting Bugs
- Use the bug report template
- Include steps to reproduce
- Describe expected vs. actual behavior
- Include browser/environment details if relevant

### Requesting Features
- Use the feature request template
- Clearly describe the feature and its benefits
- Include mockups or examples if possible

## Branching Strategy

We follow a GitFlow-inspired branching strategy:

- `main` - Production-ready code
- `develop` - Integration branch for active development
- `feature/*` - For developing new features
- `bugfix/*` - For non-critical bug fixes
- `hotfix/*` - For critical fixes needing immediate deployment
- `release/*` - For preparing releases
- `docs/*` - For documentation changes only

For complete details on workflow and processes, see our [Git Branching Strategy](docs/GIT_BRANCHING_STRATEGY.md).

## Review Process

1. All code changes require at least one review
2. Address reviewer feedback
3. Once approved, maintainers will merge your PR

## License

By contributing to Krowoc, you agree that your contributions will be licensed under the project's license. 