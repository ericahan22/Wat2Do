#!/bin/bash
set -e

# Check if we're in development mode
if [ "$PRODUCTION" != "1" ]; then
    echo "IN DEVELOMPENT MODE"
    
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
    
    echo "Starting Django development server..."
    exec python manage.py runserver 0.0.0.0:8000
else
    echo "IN PRODUCTION MODE"
    
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
    exec gunicorn \
        --bind 0.0.0.0:8000 \
        --workers 4 \
        --timeout 120 \
        --graceful-timeout 30 \
        --access-logfile - \
        --error-logfile - \
        --log-level info \
        config.wsgi:app
fi

