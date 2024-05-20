from rest_framework import serializers
from .models import Room, RoomImages, LogRoom


class RoomImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomImages
        fields =["image"]

class RoomSerializer(serializers.HyperlinkedModelSerializer):
    room_id = serializers.ReadOnlyField()
    occupied = serializers.ReadOnlyField()
    user = serializers.ReadOnlyField()
    images = RoomImageSerializer(many=True, read_only=True)
    uploaded_images = serializers.ListField(child=serializers.ImageField(allow_empty_file=False, use_url=False), write_only=True)
    available_date = serializers.ReadOnlyField()
    booked_date = serializers.ReadOnlyField()
    end_date = serializers.ReadOnlyField()
    class Meta:
        model = Room
        fields =["room_id", "name", "description", "price", "user", "room_number", "occupied", "images","uploaded_images", "url", "booked_date", "end_date", "available_date"]

    def create(self, validated_data):
        request = self.context.get('request')
        images_data = validated_data.pop("uploaded_images")
        room = Room.objects.create(**validated_data)
        for image_data in images_data:
            RoomImages.objects.create(room=room, image=image_data)
        return room
    
class LogRoomSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    booked = serializers.BooleanField(default=False)
    booked_date = serializers.DateField(format="%Y-%M-%D", input_formats=["%Y-%M-%D"])
    end_date = serializers.DateField(format="%Y-%M-%D", input_formats=["%Y-%M-%D"])
    class Meta:
        model = LogRoom
        fields =["id", "user", "room_number", "booked", "booked_date", "end_date"]


