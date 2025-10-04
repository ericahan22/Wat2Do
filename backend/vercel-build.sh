#!/bin/bash

# Install dependencies with size optimization
python3 -m pip install --no-cache-dir --disable-pip-version-check -r requirements.txt

# Clean up pip cache to reduce size
python3 -m pip cache purge || true

# Collect static files (even though we're not serving UI, Django needs this)
python3 manage.py collectstatic --noinput

# Run migrations
python3 manage.py migrate --noinput

# Create superuser if needed (uncomment if you want this)
# echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'password') if not User.objects.filter(username='admin').exists() else None" | python3 manage.py shell
