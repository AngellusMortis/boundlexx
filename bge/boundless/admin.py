from django.contrib import admin

from bge.boundless.models import Item


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ("gui_name", "id", "name")
    search_fields = ("id", "name", "gui_name")
