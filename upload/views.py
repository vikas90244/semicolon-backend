from django.shortcuts import render
from .models import UploadMetadata
from rest_framework.views import APIView
from rest_framework import status
from core.api_response import api_success
from rest_framework.exceptions import ValidationError

# Create your views here.



class InitUploadView(APIView):
    def post(self, request):
        file_name = request.data.get('filename')
        total_bytes = int(request.data.get('totalbyte'))
        total_chunks = request.data.get('totalchunks')
        chunk_size = request.data.get('chunksize')

        if not all([file_name, total_bytes, total_chunks, chunk_size]):
            raise ValidationError("filename, totalbyte, totalchunks and chunksize are required")


        # create record in database
        upload_ticket = UploadMetadata.objects.create(
            filename=file_name,
            total_chunks=total_chunks,
            size = total_bytes
        )
        rust_upload_url = f"http://localhost:9000/upload/{upload_ticket.upload_id}"

        headers = {
            'Location':rust_upload_url,
            'Access-Control-Expose-Headers': 'Location'
        }

        return api_success(
            data={
                "upload_id": str(upload_ticket.upload_id),
                "upload_url": rust_upload_url,
            },
            message="resource created successfully",
            status=201,
            headers=headers
        )