from django.contrib import admin
from bge.boundless.models import Item


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    pass
