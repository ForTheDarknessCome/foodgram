#!/usr/bin/env bash

set -e

while ! nc -z db 5432; do
    sleep 0.5
    echo "wait database"
done

echo "connected to the database"

python manage.py migrate
echo "Migrations complete"

python manage.py collectstatic --noinput
echo "Collectstatic complete"

mkdir -p /app/backend_static/static
echo "Created backend_static directory"

cp -r /app/static/. /app/backend_static/static/
echo "Static files copied to backend_static"

exec gunicorn --bind 0.0.0.0:8000 foodgram.wsgi
