# Git Branching Strategy

This document outlines our Git branching strategy to ensure consistent, reliable, and efficient development workflows.

## Branch Types

### Main Branches

- **`main`**: The production-ready branch. All code in `main` should be deployable.
- **`develop`**: The integration branch for active development. All feature branches merge into `develop`.

### Supporting Branches

- **`feature/*`**: For developing new features (e.g., `feature/user-authentication`)
- **`bugfix/*`**: For fixing bugs that aren't critical (e.g., `bugfix/form-validation-error`)
- **`hotfix/*`**: For critical fixes that need immediate deployment to production
- **`release/*`**: For preparing releases (e.g., `release/v1.2.0`)
- **`docs/*`**: For documentation changes only

## Workflow

### Feature Development

1. Create a feature branch from `develop`:
   ```
   git checkout develop
   git pull origin develop
   git checkout -b feature/feature-name
   ```

2. Develop and commit changes to the feature branch
3. When complete, create a pull request to merge into `develop`
4. After code review and approval, merge the feature into `develop`

### Bug Fixes

1. For non-critical bugs:
   - Branch from `develop`: `bugfix/bug-name`
   - Follow the same process as feature branches

2. For critical bugs (hotfixes):
   - Branch from `main`: `hotfix/bug-name`
   - Fix the issue
   - Create pull requests to merge into both `main` and `develop`

### Releases

1. When `develop` has accumulated enough features for a release:
   - Create a release branch: `release/vX.Y.Z`
   - Only bug fixes and release preparations in this branch
   - No new features

2. When ready:
   - Merge into `main` with a version tag
   - Merge back into `develop`

## Branch Protection Rules

- **`main` branch**: 
  - Require pull request reviews before merging
  - Require status checks to pass
  - No direct pushes

- **`develop` branch**:
  - Require pull request reviews
  - Require status checks to pass

## Commit Message Format

Follow the [Conventional Commits](https://www.conventionalcommits.org/) standard:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

Types:
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code changes that neither fix bugs nor add features
- `test`: Adding or improving tests
- `chore`: Changes to the build process or tools

## Tagging and Versioning

Follow [Semantic Versioning](https://semver.org/) (MAJOR.MINOR.PATCH):

- MAJOR version for incompatible API changes
- MINOR version for backward-compatible functionality
- PATCH version for backward-compatible bug fixes

Tag all releases on the `main` branch:
```
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

## Code Review Guidelines

- Review pull requests within 48 hours
- Provide constructive feedback
- Ensure tests pass and code quality standards are met
- Verify the branching strategy is followed 