#!/bin/bash
set -e

# Print which database config is selected
if [ "${PRODUCTION}" = "1" ]; then
    echo "Environment: PRODUCTION"
    echo "DB Engine: postgis (prod)"
    echo "DB Host: ${POSTGRES_HOST}"
    echo "DB Name: ${POSTGRES_DB}"
    echo "DB User: ${POSTGRES_USER}"
else
    echo "Environment: LOCAL"
    echo "DB Engine: postgis (local)"
    echo "DB Host: ${LOCAL_POSTGRES_HOST}"
    echo "DB Name: ${LOCAL_POSTGRES_DB}"
    echo "DB User: ${LOCAL_POSTGRES_USER}"
fi

# Wait for database to be ready
echo "Waiting for database..."
max_attempts=30
attempt=0
until python manage.py check --database default > /dev/null 2>&1 || [ $attempt -eq $max_attempts ]; do
    attempt=$((attempt + 1))
    echo "Database not ready, attempt $attempt/$max_attempts..."
    sleep 2
done

if [ $attempt -eq $max_attempts ]; then
    echo "ERROR: Database connection timeout after $max_attempts attempts"
    exit 1
fi

echo "Database is ready!"

echo "Running database migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting gunicorn..."
# Graceful shutdown settings:
# --graceful-timeout: Time to wait for workers to finish after SIGTERM (default 30s)
# --timeout: Worker timeout for requests (120s)
# --worker-class: Use sync workers (default)
# --access-logfile and --error-logfile: Send logs to stdout/stderr for ECS CloudWatch
exec gunicorn \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --timeout 120 \
    --graceful-timeout 30 \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    config.wsgi:app

