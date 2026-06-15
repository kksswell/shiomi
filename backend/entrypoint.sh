#!/usr/bin/env sh
set -e

python manage.py migrate --noinput
python manage.py collectstatic --noinput
python manage.py seed_defaults || true

if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ] && [ -n "$DJANGO_SUPERUSER_EMAIL" ]; then
  python manage.py createsuperuser --noinput || true
fi

exec "$@"
