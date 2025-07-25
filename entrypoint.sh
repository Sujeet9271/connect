#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Define the project directory
PROJECT_DIR="/app"

# Perform database migrations
echo "Running makemigrations..."
python3 $PROJECT_DIR/manage.py makemigrations
python3 $PROJECT_DIR/manage.py migrate

# Collect static files
echo "Collecting static files..."
python3 $PROJECT_DIR/manage.py collectstatic --no-input

# Start application server
echo "Starting application server..."
# exec python3 $PROJECT_DIR/manage.py runserver 0.0.0.0:8000
exec uvicorn core.asgi:application --host 0.0.0.0 --port 8000
