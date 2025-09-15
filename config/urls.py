# config/urls.py
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse, JsonResponse
from django.core.files.storage import default_storage
from django.db import connection
import os
import io

# Για το test του Cloudinary (προαιρετικό)
from PIL import Image  # type: ignore
try:
    from cloudinary.uploader import upload as cl_upload  # type: ignore
except Exception:
    cl_upload = None


# ---------- Health / Debug endpoints ----------
def health(_request):
    return HttpResponse("ok")


def envcheck(_request):
    # ΜΗΝ τυπώσεις μυστικά – μόνο flags
    data = {
        "DJANGO_SETTINGS_MODULE": os.environ.get("DJANGO_SETTINGS_MODULE", ""),
        "HAS_DATABASE_URL": bool(os.environ.get("DATABASE_URL")),
        "HAS_CLOUDINARY_URL": bool(os.environ.get("CLOUDINARY_URL")),
        "DEBUG": os.environ.get("DEBUG", ""),
        "ALLOWED_HOSTS": settings.ALLOWED_HOSTS,
    }
    return JsonResponse(data)


def dbcheck(_request):
    try:
        with connection.cursor() as c:
            c.execute("SELECT 1;")
        return HttpResponse("db:ok")
    except Exception as e:
        return HttpResponse(f"db:error {e}", status=500)


def storage_info(_request):
    return JsonResponse({
        "DEFAULT_FILE_STORAGE_setting": getattr(settings, "DEFAULT_FILE_STORAGE", None),
        "default_storage_class": default_storage.__class__.__name__,
        "has_CLOUDINARY_URL_env": bool(os.environ.get("CLOUDINARY_URL")),
    })


def cloudinary_test(_request):
    try:
        if cl_upload is None:
            return JsonResponse({"ok": False, "error": "cloudinary.uploader not available"}, status=500)
        # φτιάχνουμε ένα tiny JPEG στη μνήμη και το ανεβάζουμε
        img = Image.new("RGB", (2, 2), color=(255, 0, 0))
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        buf.seek(0)
        res = cl_upload(buf, folder="test", public_id="probe", overwrite=True)
        return JsonResponse({
            "ok": True,
            "public_id": res.get("public_id"),
            "url": res.get("secure_url")
        })
    except Exception as e:
        return JsonResponse({"ok": False, "error": str(e)}, status=500)


# ---------- URL patterns ----------
urlpatterns = [
    re_path(r"^healthz/?$", health, name="healthz"),
    re_path(r"^envcheck/?$", envcheck, name="envcheck"),
    re_path(r"^dbcheck/?$", dbcheck, name="dbcheck"),
    re_path(r"^storage-info/?$", storage_info, name="storage_info"),
    re_path(r"^cloudinary-test/?$", cloudinary_test, name="cloudinary_test"),

    path("admin/", admin.site.urls),
    path("", include(("posts.urls", "posts"), namespace="posts")),
]

# Σέρβις media μόνο τοπικά (DEBUG)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
