from django.contrib import admin

from boundlexx.notifications.models import (
    CreativeWorldNotification,
    DiscordWebhookSubscription,
    ExoworldExpiredNotification,
    ExoworldNotification,
    FailedTaskNotification,
    ForumCategorySubscription,
    ForumPMSubscription,
    HomeworldNotification,
    SovereignColorNotification,
    SovereignWorldNotification,
)


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "owner",
    ]


@admin.register(DiscordWebhookSubscription)
class DiscordWebhookSubscriptionAdmin(SubscriptionAdmin):
    pass


@admin.register(ForumCategorySubscription)
class ForumCategorySubscriptionAdmin(SubscriptionAdmin):
    pass


@admin.register(ForumPMSubscription)
class ForumPMSubscriptionAdmin(SubscriptionAdmin):
    pass


class NotificationAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "name",
        "active",
    ]


@admin.register(ExoworldNotification)
class ExoworldNotificationAdmin(NotificationAdmin):
    pass


@admin.register(ExoworldExpiredNotification)
class ExoworldExpiredNotificationAdmin(NotificationAdmin):
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
