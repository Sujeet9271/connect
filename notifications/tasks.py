from celery import shared_task
from accounts.models import Users
from notifications.models import Notification

@shared_task(ignore_result=True, queue='notifications')
def send_connection_notification(recipient_id:int, sender_id:int, action:str, content_type:id, object_id:id):
    try:
        recipient = Users.objects.filter(id=recipient_id).only('name').first()
        sender = Users.objects.filter(id=sender_id).only('name').first()
        if not any([recipient, sender]):
            return 'Failed to Create Notification'
        
        message = ""
        if action == "accepted":
            message = f"{sender.name} has accepted your connection request."
        elif action == "pending":
            message = f"You've a new connection request from {sender.name}"
        elif action == 'rejected':
            message = f'Your Connection request was rejected by {sender.name}'
        else:
            # extend this to create other notifications
            return 'No Action Provided'

        Notification.objects.create(
            recipient=recipient,
            sender=sender,
            message=message,
            content_type_id=content_type,
            object_id=object_id
        )

        return 'Notification Created'
    except Users.DoesNotExist:
        return 'Failed to Create Notification'
    
