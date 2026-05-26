from django.contrib import admin

from tenants.models import Client, Plant


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "created_at")


@admin.register(Plant)
class PlantAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "region", "country", "client")
    list_filter = ("client", "country")
