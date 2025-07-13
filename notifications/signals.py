from django.db.models.signals import post_save,pre_save,post_delete, pre_delete
from django.dispatch import receiver

from notifications.models import Notification

from core.logger import logger


@receiver(post_save, sender=Notification)
def post_save_notification(sender, instance:Notification, created:bool, *args, **kwargs):
    logger.debug(f'post_save_notification: {instance=}, {created=}')
    if created:
        # send email notification if required
        pass