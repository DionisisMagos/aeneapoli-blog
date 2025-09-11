from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse, JsonResponse
from django.core.files.storage import default_storage
import os

def health(_): 
    return HttpResponse("ok")

def storage_info(_):
    return JsonResponse({
        "DEFAULT_FILE_STORAGE_setting": getattr(settings, "DEFAULT_FILE_STORAGE", None),
        "default_storage_class": default_storage.__class__.__name__,
        "has_CLOUDINARY_URL_env": bool(os.environ.get("CLOUDINARY_URL")),
    })

urlpatterns = [
    re_path(r"^healthz/?$", health, name="healthz"),
    re_path(r"^storage-info/?$", storage_info, name="storage_info"),
    path("admin/", admin.site.urls),
    path("", include(("posts.urls", "posts"), namespace="posts")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
