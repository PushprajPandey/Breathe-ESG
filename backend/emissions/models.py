from django.conf import settings
from django.db import models

from ingestion.models import RawRecord, SourceType
from tenants.models import Client


class ReviewStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    APPROVED = "APPROVED", "Approved"
    FLAGGED = "FLAGGED", "Flagged"
    REJECTED = "REJECTED", "Rejected"


class EmissionFactor(models.Model):
    source_type = models.CharField(max_length=20, choices=SourceType.choices)
    category = models.CharField(max_length=100)
    subcategory = models.CharField(max_length=100, blank=True)
    factor_kgco2e_per_unit = models.DecimalField(max_digits=12, decimal_places=6)
    unit = models.CharField(max_length=20)
    year = models.PositiveIntegerField(default=2024)
    source_reference = models.CharField(max_length=255, default="DEFRA 2024")

    class Meta:
        unique_together = [["source_type", "category", "subcategory", "unit", "year"]]

    def __str__(self):
        return f"{self.category}/{self.unit}: {self.factor_kgco2e_per_unit}"


class NormalizedRecord(models.Model):
    raw_record = models.OneToOneField(
        RawRecord, on_delete=models.CASCADE, related_name="normalized", null=True, blank=True
    )
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="records")
    source_type = models.CharField(max_length=20, choices=SourceType.choices)
    activity_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)
    quantity = models.DecimalField(max_digits=16, decimal_places=4, null=True, blank=True)
    unit = models.CharField(max_length=20, blank=True)
    normalized_quantity_kwh = models.DecimalField(
        max_digits=16, decimal_places=4, null=True, blank=True
    )
    emission_factor = models.ForeignKey(
        EmissionFactor, on_delete=models.SET_NULL, null=True, blank=True
    )
    emission_kgco2e = models.DecimalField(max_digits=16, decimal_places=4, null=True, blank=True)
    scope = models.PositiveSmallIntegerField()
    review_status = models.CharField(
        max_length=20, choices=ReviewStatus.choices, default=ReviewStatus.PENDING
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    is_locked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
