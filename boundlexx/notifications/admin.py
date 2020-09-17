from django.contrib import admin

from boundlexx.notifications.models import (
    CreativeWorldNotification,
    DiscordWebhookSubscription,
    ExoworldNotification,
    FailedTaskNotification,
    HomeworldNotification,
    SovereignWorldNotification,
)


@admin.register(DiscordWebhookSubscription)
class DiscordWebhookSubscriptionAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "owner",
    ]


class WorldNotificationAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "name",
        "active",
    ]


@admin.register(ExoworldNotification)
class ExoworldNotificationAdmin(WorldNotificationAdmin):
    pass


@admin.register(SovereignWorldNotification)
class SovereignWorldNotificationAdmin(WorldNotificationAdmin):
    pass


@admin.register(CreativeWorldNotification)
class CreativeWorldNotificationAdmin(WorldNotificationAdmin):
    pass


@admin.register(HomeworldNotification)
class HomeworldNotificationAdmin(WorldNotificationAdmin):
    pass


@admin.register(FailedTaskNotification)
class FailedTaskNotificationAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "active",
    ]
