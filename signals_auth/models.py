from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from .managers import CustomUserManager
from .utils import generate_id

class User(AbstractUser):
    id  = models.CharField(primary_key=True, default=generate_id, max_length=64)
    email = models.EmailField(_("email address"), unique=True)
    fullname = models.CharField(max_length=150)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    username = None
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['fullname']

    objects = CustomUserManager()

    def __str__(self):
        return self.email