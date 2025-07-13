from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from accounts.models import ConnectionRequest, UserDetail, Users

# Register your models here.
class ProfileInline(admin.StackedInline):
    model = UserDetail
    extra = 0

@admin.register(Users)
class AccountUserAdmin(UserAdmin):
    list_display=['id', 'user_id','email','username','name', 'is_staff','is_active','date_joined']
    list_display_links=['id', 'user_id','email',]
    list_filter = ['is_active','is_staff','is_superuser','date_joined']
    readonly_fields = ('date_joined','last_login')
    search_fields = ['email','name','username']
    filter_horizontal = ('groups', 'user_permissions','connections')
    inlines = (ProfileInline, )

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('name', 'username')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Connections'), {
            'fields': ('connections',),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )


    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username','email','name', 'password1', 'password2','is_staff'),
        }),
    )


    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        else:
            return super().get_fieldsets(request, obj)
        
@admin.register(ConnectionRequest)
class ConnectionAdmin(admin.ModelAdmin):
    list_display = ['id','from_user','to_user','status','created_at','updated_at']
    list_display_links = ['id','from_user',]
    list_select_related = ['from_user','to_user']
    list_filter = ['status','created_at','updated_at']
    raw_id_fields = ['from_user','to_user']
