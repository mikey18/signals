from background_task import background
from .models import Room, LogRoom
from .serializers import RoomSerializer, LogRoomSerializer
from django.utils import timezone

@background(schedule=5)
def LogRoomTasks():
    objects = LogRoom.objects.all()
    if len(objects) != 0:
        for object in objects:
            print(object.room_number)
            room = Room.objects.get(room_number=object.room_number)
            if (object.date_booked >= room.available_date) and ( timezone.now().date >= room.date_end ):
                room.user = object.user
                room.date_booked = object.date_booked
                room.date_end = object.date_end
                room.occupied = True
                room.save()
                object.delete()
                print("room_booked")
            else:
                print("room already booked")
                continue
