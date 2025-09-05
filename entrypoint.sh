#!/usr/bin/env bash
set -e

python manage.py migrate --noinput

# optional auto-superuser: δώσε env vars στο Koyeb για να δημιουργηθεί μία φορά
python <<'PY'
import os
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()
u = os.environ.get("DJANGO_SUPERUSER_USERNAME")
p = os.environ.get("DJANGO_SUPERUSER_PASSWORD")
e = os.environ.get("DJANGO_SUPERUSER_EMAIL", "")
if u and p and not User.objects.filter(username=u).exists():
    User.objects.create_superuser(username=u, email=e, password=p)
    print("Created superuser:", u)
PY

python manage.py collectstatic --noinput

# ξεκίνα gunicorn (8080 = port στο Koyeb)
exec gunicorn config.wsgi:application --bind 0.0.0.0:8080 --workers 2
