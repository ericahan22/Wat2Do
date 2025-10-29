#!/bin/bash
set -e

# Check if we're in development mode
if [ "$PRODUCTION" != "1" ]; then
    echo "IN DEVELOMPENT MODE"
    
    # Print DB settings (redacted) for debugging
    echo "Resolved DB settings (redacted):"
    python - <<'PY'
import os
from django.conf import settings
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', os.getenv('DJANGO_SETTINGS_MODULE','config.settings.production'))
try:
    django.setup()
    cfg = settings.DATABASES['default']
    safe = {
        'ENGINE': cfg.get('ENGINE'),
        'HOST': cfg.get('HOST'),
        'PORT': cfg.get('PORT'),
        'NAME': cfg.get('NAME'),
        'USER': cfg.get('USER'),
        'OPTIONS': {k: v for k, v in (cfg.get('OPTIONS') or {}).items() if k.lower() != 'password'},
    }
    print(safe)
except Exception as e:
    print(f"Failed to load Django settings for DB: {e}")
PY

    # Wait for database to be ready
    echo "Waiting for database..."
    max_attempts=60
    attempt=0
    until python - <<'PY'
import os, sys, socket
from django.conf import settings
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', os.getenv('DJANGO_SETTINGS_MODULE','config.settings.production'))
try:
    django.setup()
    cfg = settings.DATABASES['default']
    host, port = cfg.get('HOST') or '', int(cfg.get('PORT') or 0)
    # Optional: TCP probe first if host/port provided
    if host and port:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        try:
            s.connect((host, port))
        finally:
            try: s.close()
            except: pass
    # Try actual DB connection via Django
    from django.db import connections
    with connections['default'].cursor() as c:
        c.execute('SELECT 1')
    sys.exit(0)
except Exception as e:
    print(f"DB not ready: {e}")
    sys.exit(1)
PY
    do
        attempt=$((attempt + 1))
        echo "Database not ready, attempt $attempt/$max_attempts..."
        sleep 3
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
    
    # Print DB settings (redacted) for debugging
    echo "Resolved DB settings (redacted):"
    python - <<'PY'
import os
from django.conf import settings
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', os.getenv('DJANGO_SETTINGS_MODULE','config.settings.production'))
try:
    django.setup()
    cfg = settings.DATABASES['default']
    safe = {
        'ENGINE': cfg.get('ENGINE'),
        'HOST': cfg.get('HOST'),
        'PORT': cfg.get('PORT'),
        'NAME': cfg.get('NAME'),
        'USER': cfg.get('USER'),
        'OPTIONS': {k: v for k, v in (cfg.get('OPTIONS') or {}).items() if k.lower() != 'password'},
    }
    print(safe)
except Exception as e:
    print(f"Failed to load Django settings for DB: {e}")
PY

    # Wait for database to be ready
    echo "Waiting for database..."
    max_attempts=60
    attempt=0
    until python - <<'PY'
import os, sys, socket
from django.conf import settings
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', os.getenv('DJANGO_SETTINGS_MODULE','config.settings.production'))
try:
    django.setup()
    cfg = settings.DATABASES['default']
    host, port = cfg.get('HOST') or '', int(cfg.get('PORT') or 0)
    # Optional: TCP probe first if host/port provided
    if host and port:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        try:
            s.connect((host, port))
        finally:
            try: s.close()
            except: pass
    # Try actual DB connection via Django
    from django.db import connections
    with connections['default'].cursor() as c:
        c.execute('SELECT 1')
    sys.exit(0)
except Exception as e:
    print(f"DB not ready: {e}")
    sys.exit(1)
PY
    do
        attempt=$((attempt + 1))
        echo "Database not ready, attempt $attempt/$max_attempts..."
        sleep 3
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

