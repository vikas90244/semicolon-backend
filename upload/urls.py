from django.urls import path
from .views import (
    InitUploadView, 
    ReceiveChunkView, 
    PreviousFailedUploadView,
    DownloadFileView,
    ListUploadsView
)

urlpatterns = [
    path('init-upload/', InitUploadView.as_view(), name="upload-init"),
    path('receive-chunks/<str:upload_id>/', ReceiveChunkView.as_view(), name="upload-chunks"),
    path('failed-upload/', PreviousFailedUploadView.as_view(), name="failed-uploads"),
    path('list/', ListUploadsView.as_view(), name="list-uploads"),
    path('download/<str:upload_id>/', DownloadFileView.as_view(), name="download-file"),
]