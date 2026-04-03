from rest_framework import serializers
from .models import UploadMetadata

class UploadMetadataSerializer(serializers.ModelSerializer):
    class Meta:
        model= UploadMetadata
        fields='__all__'