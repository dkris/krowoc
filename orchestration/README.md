# Krowoc Orchestration

This directory contains the Prefect workflow definitions for Krowoc's task orchestration.

## Technology Stack

- Prefect for workflow orchestration
- Python for task definitions
- Integration with Flask backend
- Background jobs processing

## Getting Started

Coming soon...

## Development

```bash
# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run Prefect server
prefect server start

# In another terminal:
# Register and run workflows
prefect deployment build
```

## Directory Structure

```
orchestration/
├── flows/           # Workflow definitions
├── tasks/           # Task definitions
├── schedules/       # Scheduled workflow triggers
└── tests/           # Unit tests for flows and tasks
``` 