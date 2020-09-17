from django.contrib import admin

from boundlexx.notifications.models import (
    DiscordWebhookSubscription,
    ExoworldNotification,
    SovereignWorldNotification,
    CreativeWorldNotification,
    FailedTaskNotification,
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


@admin.register(SovereignWorldNotification)
class SovereignWorldNotificationAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "active",
    ]


@admin.register(CreativeWorldNotification)
class CreativeWorldNotificationAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "active",
    ]


@admin.register(FailedTaskNotification)
class FailedTaskNotificationAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "active",
    ]
