#!/bin/sh

python manage.py migrate --noinput
python manage.py collectstatic --noinput

gunicorn setup.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 4 \              # ajuste conforme sua CPU (regra comum: 2×núcleos + 1)
  --timeout 120 \            # opcional, mas útil em produção
  --access-logfile "-" \     # log no stdout (útil em docker/railway/fly/etc)
  --error-logfile "-"        # log no stdout