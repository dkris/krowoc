# Migration Versions

This directory contains the Alembic migration versions for the database.

To generate a new migration:

```bash
cd backend
alembic revision --autogenerate -m "Description of the migration"
```

To upgrade the database to the latest version:

```bash
cd backend
alembic upgrade head
```

To downgrade the database to a specific version:

```bash
cd backend
alembic downgrade <revision>
``` 