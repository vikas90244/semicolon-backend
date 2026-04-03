from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@shared_task
def cleanup_stale_uploads():
    """
    Delete uploads that have been PENDING or UPLOADING for more than 7 days.
    Removes both the DB record and the partial file on disk.
    """
    from .models import UploadMetadata

    cutoff = timezone.now() - timedelta(days=7)
    stale = UploadMetadata.objects.filter(
        status__in=["PENDING", "UPLOADING"],
        created_at__lt=cutoff,
    )

    deleted_count = 0
    for upload in stale:
        # remove partial file from disk
        file_path = Path(upload.file_path)
        if file_path.exists():
            try:
                file_path.unlink()
            except OSError as e:
                logger.warning("Could not delete file %s: %s", file_path, e)

        upload.delete()
        deleted_count += 1

    logger.info("cleanup_stale_uploads: removed %d stale upload(s)", deleted_count)
    return deleted_count
