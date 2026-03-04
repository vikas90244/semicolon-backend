from django.contrib import admin
from .models import UploadMetadata


@admin.register(UploadMetadata)
class UploadMetadataAdmin(admin.ModelAdmin):
	list_display = ("filename", "size", "offset", "size", "status", "created_at")
	list_filter = ("status", "created_at")
	search_fields = ("filename",)
	readonly_fields = ("upload_id", "created_at", "updated_at")