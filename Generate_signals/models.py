from django.db import models
from django.utils import timezone
from signals_auth.models import CustomUser
from signals_auth.utils import generate_id
from django.contrib.auth.models import AbstractUser
from rest_framework_simplejwt.tokens import RefreshToken


def today():
    return timezone.now().date()

class Conncted_Clients(models.Model):
    count = models.BigIntegerField()
    
    def __str__(self):
        return self.count

class Room(models.Model):
    room_id = models.CharField(primary_key=True, default=generate_id, max_length=64)
    name = models.CharField(max_length=100, null=True, blank=True)
    description = models.CharField(max_length=1000, null=True, blank=True)
    price = models.IntegerField(blank=False, null=False)
    user = models.CharField(max_length=1000, null=True, blank=True)
    room_number = models.IntegerField(unique=True, blank=False, null=False)
    url = models.URLField()
    occupied = models.BooleanField(default=False)
    booked_date = models.DateField(default=today)
    available_date = models.DateField(default=today)
    end_date = models.DateField(default=today)
    date_created = models.DateTimeField(default=timezone.now)
    updated_date = models.DateTimeField('date_created' ,auto_now=True)


    def save(self, *args, **kwargs):
        print(self.end_date)
        self.available_date = self.end_date  + timezone.timedelta(days=1)
        super(Room, self).save(*args, **kwargs)


    def __str__(self):
        return str(self.room_number)
    
    class Meta:
        ordering = ['-room_number']


class RoomImages(models.Model):
    room = models.ForeignKey(Room, related_name="images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="media/")
    date_created = models.DateTimeField(default=timezone.now)
    updated_date = models.DateTimeField('date_created' ,auto_now=True)
    
    class Meta:
        ordering = ['-date_created']

class LogRoom(models.Model):
    id  = models.CharField(primary_key=True, default=generate_id, max_length=64)
    email = models.EmailField()
    user = models.CharField(max_length=1000, null=True, blank=True)
    room_number = models.IntegerField(blank=False, null=False)
    booked_date = models.DateField(default=today)
    end_date = models.DateField(default=today)
    booked = models.BooleanField(default=False)
    date_created = models.DateTimeField(default=timezone.now)
    updated_date = models.DateTimeField('date_created' ,auto_now=True)

    class Meta:
        ordering = ['booked_date']

    
