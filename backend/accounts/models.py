from django.contrib.auth.models import AbstractUser
from django.db import models

from tenants.models import Client


class Role(models.TextChoices):
    ADMIN = "ADMIN", "Admin"
    ANALYST = "ANALYST", "Analyst"


class CustomUser(AbstractUser):
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.ANALYST)
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name="users", null=True, blank=True
    )

    def __str__(self):
        return self.email or self.username
