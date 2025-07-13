from django.contrib import admin

from notifications.models import Notification

# Register your models here.
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['id','sender','recipient','is_read','created_at','updated_at']
    list_display_links = ['id','sender',]
    list_select_related = ['sender','recipient']
    list_filter = ['is_read','created_at','updated_at']
    raw_id_fields = ['sender', 'recipient']
