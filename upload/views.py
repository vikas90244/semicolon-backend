from .models import UploadMetadata
from rest_framework.views import APIView
from rest_framework import status
from core.api_response import api_success, api_error
from rest_framework.exceptions import ValidationError
from .parse_metadata_header import parse_metadata_header
from pathlib import Path
from rest_framework.permissions import IsAuthenticated
from .serializers import UploadMetadataSerializer
from django.conf import settings
from django.http import FileResponse, Http404
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
import os

# Create your views here.

# File upload constraints
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB
ALLOWED_EXTENSIONS = [
    '.pdf', '.doc', '.docx', '.txt', '.csv',  # Documents
    '.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg',  # Images
    '.mp4', '.avi', '.mov', '.mkv', '.webm',  # Videos
    '.mp3', '.wav', '.flac', '.ogg',  # Audio
    '.zip', '.rar', '.7z', '.tar', '.gz',  # Archives
]

UPLOAD_DIR = Path("uploads")

# Rate limiting decorator - 10 uploads per hour per user
@method_decorator(ratelimit(key='user', rate='10/h', method='POST', block=True), name='dispatch')
class InitUploadView(APIView):
    permission_classes=[IsAuthenticated,]
    
    def post(self, request):
        try:
            file_name = request.data.get('filename')
            total_bytes = int(request.data.get('totalbyte', 0))
            total_chunks = request.data.get('totalchunks')
            chunk_size = request.data.get('chunksize')
            
            # Validate required fields
            if not all([file_name, total_bytes, total_chunks, chunk_size]):
                raise ValidationError("filename, totalbyte, totalchunks and chunksize are required")
            
            # Validate file size
            if total_bytes > MAX_FILE_SIZE:
                raise ValidationError(f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB")
            
            if total_bytes <= 0:
                raise ValidationError("File size must be greater than 0")
            
            # Validate file extension
            file_ext = Path(file_name).suffix.lower()
            if file_ext not in ALLOWED_EXTENSIONS:
                raise ValidationError(
                    f"File type '{file_ext}' not allowed. "
                    f"Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
                )
            
            # Validate filename
            if len(file_name) > 255:
                raise ValidationError("Filename too long (max 255 characters)")
            
            if '..' in file_name or '/' in file_name or '\\' in file_name:
                raise ValidationError("Invalid filename")
            
            UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
            file_path = UPLOAD_DIR / f"{file_name}"

            with open(file_path, "wb") as f:
                pass
            
            # Create record in database
            upload_ticket = UploadMetadata.objects.create(
                filename=file_name,
                total_chunks=total_chunks,
                size=total_bytes,
                file_path=file_path,
                creator=request.user
            )
            
            # Use BACKEND_URL from settings
            backend_url = settings.BACKEND_URL
            upload_url = f"{backend_url}/api/upload/receive-chunks/{upload_ticket.upload_id}/"

            headers = {
                'Location': upload_url,
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
        except ValidationError as e:
            return api_error(
                message=str(e),
                code="VALIDATION_ERROR",
                status=400
            )
        except Exception as e:
            print(f"Error in InitUploadView: {e}")
            return api_error(
                message="Internal server error",
                code="INTERNAL_ERROR",
                status=500
            )

# Rate limiting for chunk uploads - 200 chunks per minute per user
@method_decorator(ratelimit(key='user', rate='200/m', method='PATCH', block=True), name='dispatch')
class ReceiveChunkView(APIView):
    permission_classes = [IsAuthenticated]
    
    def patch(self, request, upload_id):
        try:
            upload_offset = int(request.headers.get("Upload-Offset", 0))
            upload_metadata = request.headers.get("Upload-Metadata")
            input_data = request.body
            
            # Validate required parameters
            if upload_id is None or upload_metadata is None or upload_offset is None:
                raise ValidationError(
                    "upload-id, upload-metadata and upload-offset are required!"
                )
            
            # Validate upload exists and belongs to user
            try:
                upload = UploadMetadata.objects.get(upload_id=upload_id, creator=request.user)
            except UploadMetadata.DoesNotExist:
                raise ValidationError("Upload not found or unauthorized")
            
            # Validate offset
            if upload_offset < 0:
                raise ValidationError("Upload offset cannot be negative")
            
            if upload_offset > upload.size:
                raise ValidationError("Upload offset exceeds file size")
            
            # Validate chunk size (max 10MB per chunk)
            chunk_size = len(input_data)
            if chunk_size > 10 * 1024 * 1024:
                raise ValidationError("Chunk size too large (max 10MB)")
            
            metadata = parse_metadata_header(upload_metadata)
            filename = metadata.get("filename", "unknown_file")
            file_path = UPLOAD_DIR / f"{filename}"
            
            with open(file_path, "r+b") as f:
                f.seek(upload_offset)
                f.write(input_data)
                new_offset = f.tell()

            # Update upload metadata
            upload.offset = new_offset
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
                message="patched successfully!",
                status=201,
                headers=headers
            )
        except ValidationError as e:
            return api_error(
                message=str(e),
                code="VALIDATION_ERROR",
                status=400
            )
        except Exception as e:
            print(f"Error in ReceiveChunkView: {e}")
            return api_error(
                message="Internal server error",
                code="INTERNAL_ERROR",
                status=500
            )


class PreviousFailedUploadView(APIView):
    permission_classes=[IsAuthenticated, ]
    def get(self, request):
        user=request.user
        failed_uploads = UploadMetadata.objects.filter(creator=user, status="UPLOADING")
        serializer = UploadMetadataSerializer(failed_uploads, many=True)

        return api_success(
            data={
                'failed_uploads':serializer.data
            },
            message="success", 
            status=200
        )


# Rate limiting for downloads - 50 downloads per hour per user
@method_decorator(ratelimit(key='user', rate='50/h', method='GET', block=True), name='dispatch')
class DownloadFileView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, upload_id):
        """
        Download a completed upload.
        GET /api/upload/download/<upload_id>/
        
        NOTE: This stores files on local disk which works for development/demo.
        For production, you should use cloud storage (AWS S3, Google Cloud Storage, etc.)
        and generate signed URLs instead of serving files through Django.
        """
        try:
            # Get upload and verify ownership
            upload = UploadMetadata.objects.get(
                upload_id=upload_id,
                creator=request.user
            )
            
            # Only allow download of completed uploads
            if upload.status != "COMPLETED":
                return api_error(
                    message="Upload not completed yet",
                    code="NOT_COMPLETED",
                    status=400
                )
            
            # Check file exists
            file_path = Path(upload.file_path)
            if not file_path.exists():
                return api_error(
                    message="File not found on server",
                    code="FILE_NOT_FOUND",
                    status=404
                )
            
            # Return file as download
            response = FileResponse(
                open(file_path, 'rb'),
                as_attachment=True,
                filename=upload.filename
            )
            
            return response
            
        except UploadMetadata.DoesNotExist:
            return api_error(
                message="Upload not found or unauthorized",
                code="NOT_FOUND",
                status=404
            )
        except Exception as e:
            print(f"Error in DownloadFileView: {e}")
            return api_error(
                message="Internal server error",
                code="INTERNAL_ERROR",
                status=500
            )


class ListUploadsView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        List all completed uploads for current user.
        GET /api/upload/list/
        """
        uploads = UploadMetadata.objects.filter(
            creator=request.user,
            status="COMPLETED"
        ).order_by('-created_at')
        
        serializer = UploadMetadataSerializer(uploads, many=True)
        
        return api_success(
            data={'uploads': serializer.data},
            message="success",
            status=200
        )
