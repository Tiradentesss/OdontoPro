#!/bin/sh

python manage.py migrate --noinput
python manage.py collectstatic --noinput

gunicorn setup.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 4 \
  --timeout 120 \
  --access-logfile "-" \
  --error-logfile "-"