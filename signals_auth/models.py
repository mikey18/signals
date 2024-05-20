from django.db import models

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from .utils import generate_id
from .managers import CustomUserManager
from rest_framework_simplejwt.tokens import RefreshToken



class CustomUser(AbstractBaseUser, PermissionsMixin):
    id = models.CharField(primary_key=True, default=generate_id(), max_length=64)
    email = models.EmailField(_("email address"), unique=True, db_index=True)
    fullname = models.CharField(max_length=150)
    is_staff = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    date_created = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email
    
    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return{
            'refresh':str(refresh),
            'access':str(refresh.access_token)
        }