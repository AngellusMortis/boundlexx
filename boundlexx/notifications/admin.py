from django.contrib import admin

from boundlexx.notifications.models import (
    CreativeWorldNotification,
    DiscordWebhookSubscription,
    ExoworldNotification,
    FailedTaskNotification,
    HomeworldNotification,
    SovereignColorNotification,
    SovereignWorldNotification,
)


@admin.register(DiscordWebhookSubscription)
class DiscordWebhookSubscriptionAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "owner",
    ]


class NotificationAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "name",
        "active",
    ]


@admin.register(ExoworldNotification)
class ExoworldNotificationAdmin(NotificationAdmin):
    pass


@admin.register(SovereignWorldNotification)
class SovereignWorldNotificationAdmin(NotificationAdmin):
    pass


@admin.register(CreativeWorldNotification)
class CreativeWorldNotificationAdmin(NotificationAdmin):
    pass


@admin.register(HomeworldNotification)
class HomeworldNotificationAdmin(NotificationAdmin):
    pass


@admin.register(SovereignColorNotification)
class SovereignColorNotificationAdmin(NotificationAdmin):
    pass


@admin.register(FailedTaskNotification)
class FailedTaskNotificationAdmin(NotificationAdmin):
    pass
