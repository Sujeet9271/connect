from django.conf import settings
from django.db import models
from django.db.models import QuerySet
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

from django.utils import timezone
from core.logger import logger


# Create your models here.


class UserManager(BaseUserManager):

    def create_user(self, email, username, password=None, **other_fields):
        email = self.normalize_email(email)
        user  = self.model(email=email, username=username, **other_fields)
        user.set_password(password)
        user.save()
        return user
    
    
    def create_superuser(self, email, username, password=None, **other_fields):
        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_active', True)

        if other_fields.get('is_staff') is False:
            raise ValueError('Superuser must be assigned is_staff = True')

        if other_fields.get('is_superuser') is False:
            raise ValueError('Superuser must be assigned is_superuser = True')

        user = self.create_user(email=email, username=username, password=password, **other_fields)
        return user
    
    def get_queryset(self) -> QuerySet:
        return super().get_queryset()



def location(instance,filename):
    return f'profile/{instance.username.replace(' ','_')}/{filename}'


class Users(AbstractBaseUser, PermissionsMixin):
    email           = models.EmailField(verbose_name='Email', unique=True)
    username        = models.CharField(verbose_name='Username',max_length=255, unique=True)
    name            = models.CharField(verbose_name='Name', max_length=255,)
    is_active       = models.BooleanField(verbose_name='Active', default=False)
    is_staff        = models.BooleanField(verbose_name='Staff', default=False)
    is_superuser    = models.BooleanField(verbose_name='Superuser', default=False)
    date_joined     = models.DateField(verbose_name='date joined', auto_now_add=True, auto_now=False)
    profile_pic     = models.ImageField(verbose_name='Profile Image',default='profile/default_user.png', upload_to=location)

    connections     = models.ManyToManyField('self',symmetrical=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'name',]

    objects = UserManager()

    def __str__(self):
        return f'{self.email}'

    def get_fullname(self):
        return f'{self.name}'

    
    class Meta:
        db_table='users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'


class UserDetail(models.Model):
    user = models.OneToOneField(Users, on_delete=models.CASCADE, related_name='profile',primary_key=True)
    contact_number = models.CharField(max_length=20)
    company_name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    industry = models.CharField(max_length=255)

    def profile_pic_url(self):
        if self.profile_pic:
            return self.profile_pic.url
        return f"{settings.STATIC_URL}/assets_new/images/user.png"

    class Meta:
        verbose_name = "User's Detail"
        verbose_name_plural = "User's Detail"


class ConnectionRequest(models.Model):
    from_user = models.ForeignKey(Users, related_name='sent_requests', on_delete=models.CASCADE)
    to_user = models.ForeignKey(Users, related_name='received_requests', on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected','Rejected')], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'id={self.id}, from_user={self.from_user_id}, to_user={self.to_user_id}, status={self.status}'

    class Meta:
        verbose_name = "Connection Request"
        verbose_name_plural = "Connection Requests"
        # unique_together = ('from_user', 'to_user')
        ordering = ['-updated_at', 'status']
