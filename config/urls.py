from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse, JsonResponse
from django.core.files.storage import default_storage
import os
import io                     # <-- ΠΡΟΣΘΗΚΗ
from PIL import Image         # <-- ΠΡΟΣΘΗΚΗ
from cloudinary.uploader import upload as cl_upload  # type: ignore # <-- ΠΡΟΣΘΗΚΗ

def health(_):
    return HttpResponse("ok")

def storage_info(_):
    return JsonResponse({
        "DEFAULT_FILE_STORAGE_setting": getattr(settings, "DEFAULT_FILE_STORAGE", None),
        "default_storage_class": default_storage.__class__.__name__,
        "has_CLOUDINARY_URL_env": bool(os.environ.get("CLOUDINARY_URL")),
    })

def cloudinary_test(_):
    try:
        # φτιάχνουμε ένα tiny JPEG στη μνήμη και το ανεβάζουμε
        img = Image.new("RGB", (2, 2), color=(255, 0, 0))
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        buf.seek(0)
        res = cl_upload(buf, folder="test", public_id="probe", overwrite=True)
        return JsonResponse({"ok": True,
                             "public_id": res.get("public_id"),
                             "url": res.get("secure_url")})
    except Exception as e:
        return JsonResponse({"ok": False, "error": str(e)}, status=500)

urlpatterns = [
    re_path(r"^healthz/?$", health, name="healthz"),
    re_path(r"^storage-info/?$", storage_info, name="storage_info"),
    re_path(r"^cloudinary-test/?$", cloudinary_test, name="cloudinary_test"),
    path("admin/", admin.site.urls),
    path("", include(("posts.urls", "posts"), namespace="posts")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
