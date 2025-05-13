# Getting Started with Krowoc Development

This guide will help you set up the Krowoc development environment on your local machine.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/)
- [Node.js](https://nodejs.org/) (v18 or later)
- [Python](https://www.python.org/) (v3.11 or later)
- [Git](https://git-scm.com/)

## Setup Steps

### 1. Clone the Repository

```bash
git clone <repository-url>
cd krowoc
```

### 2. Environment Configuration

Create a `.env` file in the root directory by copying the example file:

```bash
cp _env.example .env
```

Then edit the `.env` file to add your own API keys and configuration values.

### 3. Start the Development Environment

You can start the entire development environment using Docker Compose:

```bash
docker-compose up
```

Or run individual services for development:

#### Backend (Flask)

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
flask run
```

#### Frontend (Next.js)

```bash
cd frontend
npm install
npm run dev
```

#### Orchestration (Prefect)

```bash
cd orchestration
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
prefect server start
```

### 4. Initialize the Database

Set up the database using Alembic migrations:

```bash
cd backend
alembic upgrade head
```

### 5. Access the Application

- Frontend: http://localhost:3000
- Backend API: http://localhost:5000
- Prefect UI: http://localhost:4200

## Development Workflow

### Frontend Development

1. Create new components in the `frontend/components` directory
2. Add new pages in the `frontend/pages` directory
3. Style with Tailwind CSS classes

### Backend Development

1. Create new models in the `backend/models` directory
2. Add API endpoints to the appropriate files in `backend/api`
3. Generate migrations after model changes:
   ```bash
   alembic revision --autogenerate -m "Description of changes"
   ```

### Testing

Run tests for each component:

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## Troubleshooting

### Common Issues

1. **Database Connection Issues**
   - Check that Postgres is running and accessible
   - Verify your DATABASE_URL in the .env file

2. **Frontend Build Errors**
   - Make sure all dependencies are installed
   - Check for TypeScript errors

3. **Docker Issues**
   - Try rebuilding the containers: `docker-compose build --no-cache`
   - Check container logs: `docker-compose logs <service-name>`

## Getting Help

- Check the project documentation in the `docs` directory
- Review the code repository for examples
- Consult the [Project Status](../../PROJECT_STATUS.md) document for current development focus 