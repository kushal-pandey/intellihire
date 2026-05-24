#!/bin/bash
set -e

echo "Running Django migrations..."
python manage.py migrate --run-syncdb

echo "Creating superuser if not exists..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
U = get_user_model()
if not U.objects.filter(username='admin').exists():
    U.objects.create_superuser('admin', 'admin@intellihire.com', 'admin123')
    print('Superuser created.')
else:
    print('Superuser already exists.')
"

echo "Starting Django with gunicorn..."
gunicorn intellihire_admin.wsgi:application --bind "0.0.0.0:${PORT:-8001}" --workers 2