#!/usr/bin/env bash

set -e

while ! nc -z db 5432; do
    sleep 0.5
    echo "wait database"
done

python manage.py migrate
python manage.py collectstatic --noinput
python manage.py create_superuser

mkdir -p /app/backend_static/static

cp -r /app/static/. /app/backend_static/static/


exec gunicorn --bind 0.0.0.0:8000 foodgram.wsgi
