from rest_framework import serializers
from notifications.models import Notification



class NotificationSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.name', read_only=True)

    class Meta:
        model = Notification
        fields = ['id', 'sender_name', 'message', 'is_read', 'created_at']
