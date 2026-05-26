from django.db import models


class Client(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Plant(models.Model):
    """SAP WERKS plant code lookup — codes are meaningless without this table."""

    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name="plants", null=True, blank=True
    )
    code = models.CharField(max_length=10, db_index=True)
    name = models.CharField(max_length=255)
    region = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=50, blank=True, default="")

    class Meta:
        ordering = ["code"]
        unique_together = [["code", "client"]]

    def __str__(self):
        return f"{self.code} — {self.name}"
