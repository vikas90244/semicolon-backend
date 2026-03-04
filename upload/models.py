from django.db import models
from uuid import uuid4

# Create your models here.


class UploadMetadata(models.Model):
    upload_id = models.UUIDField( primary_key= True,  default= uuid4, editable= False )
    filename = models.CharField(max_length=255)

    file_path = models.CharField(max_length=500)

    total_chunks = models.IntegerField()
    offset = models.IntegerField(default=0)
    size = models.BigIntegerField()

    STATUS_CHOICES = [
            ('PENDING', 'Pending'),
            ('UPLOADING', 'Uploading'),
            ('COMPLETED', 'Completed'),
            ('FAILED', 'Failed'),
        ]
    status = models.CharField(
        max_length=20,
        choices = STATUS_CHOICES,
        default='PENDING'
    )


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
            return f"{self.filename}"
