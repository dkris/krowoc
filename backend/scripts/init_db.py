#!/usr/bin/env python3
import os
import subprocess
import time
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://krowoc:krowoc@localhost:5432/krowoc")

def wait_for_db():
    """Wait for the database to be ready."""
    print("Waiting for database to be ready...")
    engine = create_engine(DATABASE_URL)
    max_retries = 30
    retry_interval = 2

    for i in range(max_retries):
        try:
            # Try to connect to the database
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                print("Database is ready!")
                return True
        except OperationalError:
            print(f"Database not ready yet. Retry {i+1}/{max_retries}...")
            time.sleep(retry_interval)
    
    print("Failed to connect to the database after multiple retries")
    return False

def run_migrations():
    """Run Alembic migrations."""
    print("Running database migrations...")
    # Change to the directory where alembic.ini is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.dirname(script_dir)
    
    try:
        subprocess.run(["alembic", "upgrade", "head"], check=True, cwd=backend_dir)
        print("Migrations completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Migration failed: {e}")
        return False

def create_initial_migration():
    """Create an initial migration if none exists."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.dirname(script_dir)
    versions_dir = os.path.join(backend_dir, "migrations", "versions")
    
    # Check if there are any migration files (excluding README)
    migration_files = [f for f in os.listdir(versions_dir) if f.endswith('.py')]
    
    if not migration_files:
        print("No migration files found. Creating initial migration...")
        try:
            subprocess.run(
                ["alembic", "revision", "--autogenerate", "-m", "initial_migration"], 
                check=True, 
                cwd=backend_dir
            )
            print("Initial migration created successfully!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Failed to create initial migration: {e}")
            return False
    else:
        print(f"Found {len(migration_files)} existing migration files. Skipping initial migration creation.")
        return True

if __name__ == "__main__":
    if wait_for_db():
        if create_initial_migration():
            run_migrations()
    else:
        print("Database initialization failed.") 