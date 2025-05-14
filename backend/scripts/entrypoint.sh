#!/bin/bash
set -e

# Run database initialization script
echo "Initializing database..."
python scripts/init_db.py

# Start the Flask application
echo "Starting Flask application..."
exec flask run --host=0.0.0.0 