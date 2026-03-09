#!/bin/sh
set -e

python manage.py migrate --noinput
python manage.py collectstatic --noinput --clear

gunicorn setup.asgi:application \
  -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:$PORT
  --workers 3 \               # <- adicione isso (ajuste conforme CPU/memória do plano)
  --timeout 120 \             # <- útil se tiver tarefas longas
  --log-level info