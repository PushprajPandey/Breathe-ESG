from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from accounts.models import Role
from emissions.models import EmissionFactor
from ingestion.models import SourceType
from tenants.models import Client, Plant

User = get_user_model()

FACTORS = [
    ("sap", "diesel", "L", "2.687"),
    ("sap", "natural_gas", "M3", "2.05"),
    ("sap", "lpg", "KG", "3.02"),
    ("sap", "heavy_fuel_oil", "GAL", "10.21"),
    ("utility", "grid_electricity", "kWh", "0.207"),
    ("utility", "grid_electricity", "Maharashtra", "kWh", "0.82"),
    ("travel", "flight", "km", "0.255"),
    ("travel", "rail", "km", "0.035"),
    ("travel", "car", "km", "0.17"),
    ("travel", "hotel", "nights", "25.0"),
]


class Command(BaseCommand):
    help = "Seed demo client, users, and emission factors"

    def handle(self, *args, **options):
        client, _ = Client.objects.get_or_create(
            slug="global-org-corp",
            defaults={"name": "Global Org Corp"},
        )
        admin, created = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@breatheesg.com",
                "role": Role.ADMIN,
                "client": client,
                "is_staff": True,
            },
        )
        if created:
            admin.set_password("admin123")
            admin.save()
        analyst, created = User.objects.get_or_create(
            username="analyst",
            defaults={
                "email": "analyst@breatheesg.com",
                "role": Role.ANALYST,
                "client": client,
            },
        )
        if created:
            analyst.set_password("analyst123")
            analyst.save()

        plants = [
            ("4521", "Mumbai Refinery", "Maharashtra", "IN"),
            ("2041", "Delhi Distribution Hub", "NCR", "IN"),
            ("1021", "Pune Manufacturing", "Maharashtra", "IN"),
            ("2011", "Chennai Operations", "Tamil Nadu", "IN"),
        ]
        for code, name, region, country in plants:
            Plant.objects.get_or_create(
                code=code,
                client=client,
                defaults={"name": name, "region": region, "country": country},
            )

        for entry in FACTORS:
            if len(entry) == 4:
                source, cat, unit, factor = entry
                subcategory = ""
            else:
                source, cat, subcategory, unit, factor = entry
            EmissionFactor.objects.get_or_create(
                source_type=source,
                category=cat,
                subcategory=subcategory,
                unit=unit,
                year=2024,
                defaults={
                    "factor_kgco2e_per_unit": Decimal(factor),
                    "source_reference": "CEA India 2024" if subcategory == "Maharashtra" else "DEFRA 2024",
                },
            )

        self.stdout.write(self.style.SUCCESS("Seed complete: admin/admin123, analyst/analyst123"))
