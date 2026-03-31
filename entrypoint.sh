#!/bin/bash
# entrypoint.sh — Waits for PostgreSQL readiness before running migrations.
set -e

echo "Waiting for PostgreSQL..."
while ! nc -z db 5432; do
    sleep 0.5
done
echo "PostgreSQL ready."

python manage.py migrate --no-input
python manage.py collectstatic --no-input 2>/dev/null || true

exec "$@"
