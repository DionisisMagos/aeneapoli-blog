# api/index.py
import os
from asgiref.wsgi import WsgiToAsgi
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
app = WsgiToAsgi(get_wsgi_application())
