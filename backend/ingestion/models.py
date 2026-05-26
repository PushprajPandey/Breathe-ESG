from django.conf import settings
from django.db import models

from tenants.models import Client


class SourceType(models.TextChoices):
    SAP = "sap", "SAP (Scope 1)"
    UTILITY = "utility", "Utility (Scope 2)"
    TRAVEL = "travel", "Travel (Scope 3)"


class UploadStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    PROCESSING = "PROCESSING", "Processing"
    COMPLETED = "COMPLETED", "Completed"
    FAILED = "FAILED", "Failed"


class ParseStatus(models.TextChoices):
    SUCCESS = "SUCCESS", "Success"
    FAILED = "FAILED", "Failed"
    SUSPICIOUS = "SUSPICIOUS", "Suspicious"


class FileUpload(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="uploads")
    source_type = models.CharField(max_length=20, choices=SourceType.choices)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file_path = models.FileField(upload_to="uploads/%Y/%m/")
    status = models.CharField(
        max_length=20, choices=UploadStatus.choices, default=UploadStatus.PENDING
    )
    rows_parsed = models.PositiveIntegerField(default=0)
    rows_failed = models.PositiveIntegerField(default=0)
    rows_suspicious = models.PositiveIntegerField(default=0)
    rows_truncated = models.BooleanField(default=False)

    class Meta:
        ordering = ["-uploaded_at"]


class RawRecord(models.Model):
    upload = models.ForeignKey(FileUpload, on_delete=models.CASCADE, related_name="raw_records")
    raw_data = models.JSONField()
    row_number = models.PositiveIntegerField()
    parse_status = models.CharField(
        max_length=20, choices=ParseStatus.choices, default=ParseStatus.SUCCESS
    )
    parse_error = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["row_number"]
