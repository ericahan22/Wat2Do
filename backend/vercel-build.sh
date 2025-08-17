#!/bin/bash

# Install dependencies
pip install -r requirements.txt

# Collect static files (even though we're not serving UI, Django needs this)
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate --noinput

# Create superuser if needed (uncomment if you want this)
# echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'password') if not User.objects.filter(username='admin').exists() else None" | python manage.py shell
