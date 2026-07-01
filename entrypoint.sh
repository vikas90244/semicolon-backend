#!/bin/bash
set -e

echo "Running database migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput || true

echo "Creating demo user (if not exists)..."
python manage.py create_demo_user || echo "Demo user already exists or failed"

echo "Starting Gunicorn server on port ${PORT:-8000}..."
exec gunicorn core.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 2 --timeout 300 --keep-alive 5
