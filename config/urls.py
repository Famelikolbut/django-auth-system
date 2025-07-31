from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    # ИСПОЛЬЗУЕМ ПОЛНЫЕ ПУТИ
    path("api/auth/", include("apps.users.urls")),
    path("api/", include("apps.documents.urls")),
    path("api/admin/", include("apps.users.admin_urls")),
]
