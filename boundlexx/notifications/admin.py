from django.contrib import admin

from boundlexx.notifications.models import (
    DiscordWebhookSubscription,
    ExoworldNotification,
)


@admin.register(DiscordWebhookSubscription)
class DiscordWebhookSubscriptionAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "owner",
    ]


@admin.register(ExoworldNotification)
class ExoworldNotificationAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "active",
    ]
