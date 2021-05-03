def send_exo_notifcation(world_or_poll, is_update=False):
    from boundlexx.notifications.models import (  # pylint: disable=cyclic-import
        ExoworldNotification,
    )

    if is_update:
        ExoworldNotification.objects.send_update_notification(world_or_poll)
    else:
        ExoworldNotification.objects.send_new_notification(world_or_poll)


def send_color_update_notification(item, colors, new_ids):
    from boundlexx.notifications.models import (  # pylint: disable=cyclic-import
        SovereignColorNotification,
    )

    SovereignColorNotification.objects.send_notification(
        item,
        colors,
        new_ids,
    )
