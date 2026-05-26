from django.conf import settings
from django.db import models

from emissions.models import NormalizedRecord


class AuditAction(models.TextChoices):
    CREATED = "CREATED", "Created"
    APPROVED = "APPROVED", "Approved"
    FLAGGED = "FLAGGED", "Flagged"
    REJECTED = "REJECTED", "Rejected"
    BULK_APPROVED = "BULK_APPROVED", "Bulk Approved"
    UPLOADED = "UPLOADED", "Uploaded"
    PARSED = "PARSED", "Parsed"


class AuditLog(models.Model):
    record = models.ForeignKey(
        NormalizedRecord,
        on_delete=models.CASCADE,
        related_name="audit_logs",
        null=True,
        blank=True,
    )
    action = models.CharField(max_length=30, choices=AuditAction.choices)
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    performed_at = models.DateTimeField(auto_now_add=True)
    before_state = models.JSONField(null=True, blank=True)
    after_state = models.JSONField(null=True, blank=True)
    message = models.TextField(blank=True)

    class Meta:
        ordering = ["-performed_at"]


class ApprovalRecord(models.Model):
    record = models.ForeignKey(NormalizedRecord, on_delete=models.CASCADE)
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    approved_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
