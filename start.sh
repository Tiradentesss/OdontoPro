#!/bin/sh
set -e

echo "=== START.SH INICIADO ==="
echo "PORT fornecido pelo Railway: ${PORT:-'NÃO DEFINIDO'}"

python manage.py migrate --noinput || echo "Migrate falhou ou pulado"

# Remova --clear para não apagar tudo toda vez
python manage.py collectstatic --noinput || echo "Collectstatic falhou ou pulado"

echo "=== INICIANDO GUNICORN ==="
echo "Bind: 0.0.0.0:${PORT}"

# Tente primeiro com IPv4 (mais comum no Railway)
exec gunicorn setup.asgi:application \
  --bind "0.0.0.0:${PORT}" \
  -k uvicorn.workers.UvicornWorker \
  --workers 2 \          # aumente se tiver mais RAM
  --timeout 120 \
  --log-level info       # debug gera muito log, mude para info em prod