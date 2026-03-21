#!/usr/bin/env bash
set -e

python manage.py migrate --noinput

# auto-superuser με σωστή αρχικοποίηση Django
python <<'PY'
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()
u = os.environ.get("DJANGO_SUPERUSER_USERNAME")
p = os.environ.get("DJANGO_SUPERUSER_PASSWORD")
e = os.environ.get("DJANGO_SUPERUSER_EMAIL", "")
if u and p:
    if not User.objects.filter(username=u).exists():
        User.objects.create_superuser(username=u, email=e, password=p)
        print("Created superuser:", u)
    else:
        print("Superuser already exists:", u)
PY

python manage.py collectstatic --noinput

# ξεκίνα gunicorn
exec gunicorn config.wsgi:application --bind 0.0.0.0:8080 --workers 2
