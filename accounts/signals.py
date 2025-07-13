from django.db.models.signals import post_save,pre_save,post_delete, pre_delete
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import smart_bytes
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import EmailMessage
from django.core.exceptions import ValidationError

from accounts.models import ConnectionRequest, Users
from accounts.tasks import send_confirmation_mail
from notifications.models import Notification
from notifications.tasks import send_connection_notification

from core.logger import logger



def generate_unique_user_id():
    prefix = 'USR'
    last_user = Users.objects.exclude(user_id__isnull=True).order_by('-id').first()
    if last_user and last_user.user_id:
        try:
            last_num = int(last_user.user_id.replace(prefix, ''))
        except ValueError:
            last_num = 0
    else:
        last_num = 0
    return f"{prefix}{last_num + 1:05d}"

@receiver(pre_save, sender=Users)
def pre_save_users(sender, instance:Users, *args, **kwargs):
    logger.info('pre_save_user')
    if not instance.user_id:
        user_id = generate_unique_user_id()
        logger.info(f'{user_id=}')
        instance.user_id = user_id



@receiver(post_save,sender=Users)
def post_save_user(sender, instance:Users, created:bool, *args, **kwargs):
    logger.info('post_save_user')
    try:
        if created and not instance.is_active:
            send_confirmation_mail.delay(user_id=instance.id)
            
    except Exception as e:
        logger.exception(stack_info=False, msg=f"Exception={e.args}")

@receiver(pre_save, sender=ConnectionRequest)
def pre_save_connection_request(sender, instance:ConnectionRequest, *args, **kwargs):
    logger.debug('pre_save_connection_request')
    if instance.pk:
        return

    from_user = instance.from_user
    to_user = instance.to_user

    # Check if any connection (pending or accepted) already exists in either direction
    existing_request = ConnectionRequest.objects.filter(
        Q(from_user=from_user, to_user=to_user) | Q(from_user=to_user, to_user=from_user),
        status__in=['pending', 'accepted']
    ).exists()

    if existing_request:
        raise ValidationError("A connection already exists or is pending between these users.")



@receiver(post_save, sender=ConnectionRequest)
def post_save_connection_request(sender, instance:ConnectionRequest, created:bool, *args, **kwargs):
    logger.debug('post_save_connection_request')
    content_type = ContentType.objects.get_for_model(sender)
    if created:
        send_connection_notification.delay(recipient_id=instance.to_user_id, sender_id=instance.from_user_id, action=instance.status, content_type=content_type.id, object_id=instance.id)
    elif instance.status == 'accepted':
        send_connection_notification.delay(recipient_id=instance.from_user_id, sender_id=instance.to_user_id, action=instance.status, content_type=content_type.id, object_id=instance.id)
        instance.from_user.connections.add(instance.to_user)
    elif instance.status == 'rejected':
        send_connection_notification.delay(recipient_id=instance.from_user_id, sender_id=instance.to_user_id, action=instance.status, content_type=content_type.id, object_id=instance.id)


@receiver(post_delete, sender=ConnectionRequest)
def post_delete_connection_request(sender, instance:ConnectionRequest, *args, **kwargs):
    logger.debug('post_delete_connection_request')
    content_type = ContentType.objects.get_for_model(sender)
    Notification.objects.filter(content_type=content_type, object_id=instance.id).delete()