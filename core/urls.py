"""
URL configuration for core project.
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse





urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/users/", include("users.urls")),
    path("api/upload/", include("upload.urls")),
]
