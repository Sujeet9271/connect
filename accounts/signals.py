from django.db.models.signals import post_save,pre_save,post_delete, pre_delete
from django.dispatch import receiver

from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import smart_bytes
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import EmailMessage

from accounts.models import ConnectionRequest, Users
from accounts.tasks import send_confirmation_mail
from notifications.tasks import send_connection_notification

from core.logger import logger

@receiver(post_save,sender=Users)
def post_save_user(sender, instance:Users, created:bool, *args, **kwargs):
    logger.info('post_save_user')
    try:
        if created and not instance.is_active:
            send_confirmation_mail.delay(user_id=instance.id)
            
    except Exception as e:
        logger.exception(stack_info=False, msg=f"Exception={e.args}")

@receiver(post_save, sender=ConnectionRequest)
def post_save_connection_request(sender, instance:ConnectionRequest, created:bool, *args, **kwargs):
    if created:
        send_connection_notification.delay(recipient_id=instance.to_user_id, sender_id=instance.from_user_id, action=instance.status)
    
    if instance.status == 'accepted':
        instance.from_user.connections.add(instance.to_user)
