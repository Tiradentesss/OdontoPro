#!/bin/sh
set -e

<<<<<<< HEAD
echo "=== START.SH INICIADO ==="
echo "PORT value is: ${PORT:-'NOT SET'}"
echo "Fallback port will be used if empty: 8080"
=======

python manage.py migrate --noinput || echo "Migrate skipped or failed"
python manage.py collectstatic --noinput --clear || echo "Collectstatic skipped or failed"

echo "=== INICIANDO GUNICORN AGORA ==="
echo "Bind command: 0.0.0.0:${PORT:-8080}"

exec gunicorn setup.asgi:application \
  --bind "0.0.0.0:${PORT:-8080}" \
  -k uvicorn.workers.UvicornWorker \
<<<<<<< HEAD
  --workers 1 \
  --timeout 120 \
  --log-level debug
=======
  --bind 0.0.0.0:$PORT
>>>>>>> parent of fad349b (port upd)
