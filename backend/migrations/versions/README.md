# Migration Versions

This directory contains database migration versions managed by Alembic.

## Migration Commands

To generate a new migration:
```
alembic revision --autogenerate -m "description of changes"
```

To apply migrations:
```
alembic upgrade head
```

To downgrade:
```
alembic downgrade -1
```

## Current Schema

The current schema includes:
- users
- prompts
- api_keys
- executions 