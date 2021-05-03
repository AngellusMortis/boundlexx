import logging

from django.db import transaction
from huey.contrib.djhuey import db_task

from boundlexx.boundless.models import World

logger = logging.getLogger("huey")


@db_task()
def set_notification_sent(world_id, sent):
    with transaction.atomic():
        world = World.objects.filter(id=world_id).select_for_update().first()

        if world is not None:
            world.notification_sent = sent
            world.save()
            logger.info(
                "Setting notification sent for %s, status: %s",
                world,
                world.notification_sent,
            )

            world.refresh_from_db()
            logger.info(
                "Notification sent after refresh for %s, status: %s",
                world,
                world.notification_sent,
            )
