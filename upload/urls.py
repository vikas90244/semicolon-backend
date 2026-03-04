from django.urls import path
from .views import InitUploadView, ReceiveChunkView

urlpatterns = [
    path('init', InitUploadView.as_view(), name="upload-init"),
    path('receive-chunks', ReceiveChunkView.as_view(), name="upload-metadata" )
]