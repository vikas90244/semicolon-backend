from django.urls import path
from .views import InitUploadView

urlpatterns = [
    path('init', InitUploadView.as_view(), name="upload-init")
]