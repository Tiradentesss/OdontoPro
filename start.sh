#!/usr/bin/env bash

set -e

echo "=== DEBUG START ==="
echo "Current user: $(whoami)"
echo "Working dir: $(pwd)"
echo "PORT from env: '${PORT}'"   # Deve mostrar um número! Se vazio → problema
if [ -z "$PORT" ]; then
  echo "WARNING: PORT is empty! Using fallback 8080 for debug"
  PORT=8080
fi
echo "Final bind port will be: $PORT"

python manage.py migrate --noinput || echo "Migrate failed, continuing..."
python manage.py collectstatic --noinput --clear || echo "Collectstatic failed, continuing..."

echo "Starting Gunicorn with debug..."
exec gunicorn setup.asgi:application \
  --bind "0.0.0.0:${PORT}" \
  -k uvicorn.workers.UvicornWorker \
  --workers 1 \               # Comece com 1 worker pra economizar memória
  --timeout 180 \
  --log-level debug \
  --capture-output \
  --enable-stdio-inheritance   # Força mais logs

echo "Gunicorn exited unexpectedly"  # Não deve chegar aqui