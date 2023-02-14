from django.db import models
from .managers import CustomUserManager
from django.contrib.auth.models import AbstractUser
from datetime import datetime
import django.utils.timezone
from taggit.managers import TaggableManager

class User(AbstractUser):

    def image_upload(instance,title):
        return f'user/{instance.username}/profile/{instance.profile_pic}'
    
    def cover_pic_upload(instance,title):
        return f'user/{instance.username}/coverpic/{instance.cover_pic}'

    username = models.CharField(max_length = 50,unique = True)
    email = models.EmailField(unique = True)
    phone = models.CharField(max_length = 10,null=True)
    profile_pic = models.ImageField(upload_to= image_upload,null=True)
    cover_pic = models.ImageField(upload_to= cover_pic_upload,null=True)
    tags= TaggableManager()
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)
    date_joined = models.DateField(default = django.utils.timezone.now)
    updated_at =models.DateTimeField(default=datetime.now())

    object = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username