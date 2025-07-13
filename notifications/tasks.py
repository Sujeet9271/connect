from celery import shared_task
from accounts.models import Users
from notifications.models import Notification

@shared_task
def send_connection_notification(recipient_id, sender_id, action):
    try:
        recipient = Users.objects.get(id=recipient_id)
        sender = Users.objects.get(id=sender_id)
    except Users.DoesNotExist:
        return
    
    message = ""
    if action == "accepted":
        message = f"{sender.name} has accepted your connection request."
    elif action == "pending":
        message = f"You've a new connection request from {sender.name}"
    else:
        return  # Unknown action

    Notification.objects.create(
        recipient=recipient,
        sender=sender,
        message=message
    )
