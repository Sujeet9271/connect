from django.db import models
from accounts.models import Users


# Create your models here.
class Notification(models.Model):
    recipient = models.ForeignKey(Users, related_name='notifications', on_delete=models.CASCADE)
    sender = models.ForeignKey(Users, related_name='sent_notifications', on_delete=models.SET_NULL, null=True)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']


    def read(self):
        if not self.is_read:
            self.is_read = True
            self.save(update_fields=['is_read', 'updated_at'])
        return self