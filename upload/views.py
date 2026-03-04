from django.shortcuts import render
from .models import UploadMetadata
from rest_framework.views import APIView
from rest_framework import status
from core.api_response import api_success
from rest_framework.exceptions import ValidationError
from .parse_metadata_header import parse_metadata_header
from pathlib import Path
from .models import UploadMetadata
# Create your views here.


UPLOAD_DIR = Path("uploads")

class InitUploadView(APIView):
    def post(self, request):
        try:
            file_name = request.data.get('filename')
            total_bytes = int(request.data.get('totalbyte'))
            total_chunks = request.data.get('totalchunks')
            chunk_size = request.data.get('chunksize')

            if not all([file_name, total_bytes, total_chunks, chunk_size]):
                raise ValidationError("filename, totalbyte, totalchunks and chunksize are required")
            
            UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
            file_path = UPLOAD_DIR / f"{file_name}"


            with open(file_path, "wb") as f:
                pass
            # create record in database
            upload_ticket = UploadMetadata.objects.create(
                filename=file_name,
                total_chunks=total_chunks,
                size = total_bytes,
                file_path=file_path
            )
            upload_url = f"http://localhost:8000/api/upload/receive-chunks/{upload_ticket.upload_id}"

            headers = {
                'Location':upload_url,
                'Access-Control-Expose-Headers': 'Location'
            }

            return api_success(
                data={
                    "upload_id": str(upload_ticket.upload_id),
                    "upload_url": upload_url,
                },
                message="resource created successfully",
                status=201,
                headers=headers
            )
        except Exception as e:
            print(e)

class ReceiveChunkView(APIView):
    def patch(self, request):
        try:
            upload_offset = int(request.headers.get("Upload-Offset"))
            upload_id = request.headers.get("Upload-Id")
            upload_metadata = request.headers.get("Upload-Metadata")
            input_data = request.body
            """
            raise Validation Error if any of these are missing!
            """
            if upload_id is None or upload_metadata is None or upload_offset is None:
                raise ValidationError(
                    "upload-id, upload-metadata and upload-offset header values are required!"
                )
            
            metadata = parse_metadata_header(upload_metadata)
            filename = metadata.get("filename", "unknown_file")
            file_path = UPLOAD_DIR / f"{filename}"
            with open(file_path, "r+b") as f:
                f.seek(upload_offset)
                f.write(input_data)
                new_offset = f.tell()

            """
            update upload-metadata model
            """
            upload=UploadMetadata.objects.get(upload_id=upload_id)
            upload.offset= new_offset
            if new_offset >= upload.size:
                upload.status = "COMPLETED"
            else:
                upload.status = "UPLOADING"
            upload.save(update_fields=["offset", "status"])

            headers = {
                'Upload-Offset': str(new_offset),
                "Access-Control-Expose-Headers": "Upload-Offset"
            }

            return api_success(
                message="patched successfully! ",
                status=201,
                headers=headers
            )
        except Exception as e:
            print(e)