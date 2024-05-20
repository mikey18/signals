from django.shortcuts import render
from django.http import HttpResponse, Http404, JsonResponse

from django.http import Http404, JsonResponse
from rest_framework.generics import (CreateAPIView, ListAPIView, RetrieveAPIView,
                                        UpdateAPIView, DestroyAPIView, GenericAPIView)
from .models import Room, LogRoom

from rest_framework.parsers import JSONParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from .serializers import RoomSerializer, LogRoomSerializer
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser, FileUploadParser
import django_filters
from .tasks import LogRoomTasks

from datetime import datetime, date
from drf_spectacular.utils import extend_schema






class RoomFilter(django_filters.FilterSet):
    available_date = django_filters.DateFilter(field_name='available_date', lookup_expr='gte')
    occupied = django_filters.BooleanFilter(field_name='occupied')
    booked_date = django_filters.DateFilter(field_name='booked_date', lookup_expr='exact')
    class Meta:
        model = Room
        fields = ['available_date', 'occupied', 'booked_date']


class AllRoom(ListAPIView):
    """Lists all Rooms from the database"""
    #permission_classes = [IsAdminUser]
    serializer_class = RoomSerializer
    # filterset_class = RoomFilter
    # filter_backends = [DjangoFilterBackend]
    # filterset_fields = ['available_date']

    @extend_schema()
    def get_queryset(self):
        querys = Room.objects.all()
        # if date != None:
        # try:
        if self.request.GET.get('date_begin') == None and self.request.GET.get('end_date') == None:
            return querys
        else:
            begin_date = self.request.GET.get('date_begin').split('-')  #date.split('-')
            end_date = self.request.GET.get('end_date').split('-')  #date.split('-')

            value1 = date(int(begin_date[0]), int(begin_date[1]), int(begin_date[2])) #self.request.query_params.get('available_date')
            value2 = date(int(end_date[0]), int(end_date[1]), int(end_date[2]))
            objects = []
            for query in querys:
                logroom = LogRoom.objects.filter(room_number=query.room_number)
                if len(logroom) != 0:
                    for log in logroom:
                        cond1 = (value1 >= query.booked_date and value1 <= query.end_date)  and (value1 >= log.booked_date and value1 <= log.end_date)
                        cond2 = (value2 >= query.booked_date and value2 <= query.end_date)  and (value2 >= log.booked_date and value2 <= log.end_date)

                        if (not cond1):
                            if (value1 < query.booked_date) and (value2 < query.booked_date) and (value1 < log.booked_date) and (value2 < log.booked_date):
                                objects.append(query)
                            elif (value1 > query.end_date) and (value2 > query.end_date) and (value1 > log.end_date) and (value2 > log.end_date):
                                objects.append(query)
                            else:
                                continue
                elif len(logroom) == 0:
                    cond1 = (value1 >= query.booked_date and value1 <= query.end_date)
                    cond2 = (value2 >= query.booked_date and value2 <= query.end_date) 
                    if (not cond1) :
                        if (value1 < query.booked_date) and (value2 < query.booked_date):
                            objects.append(query)
                        elif (value1 > query.end_date) and (value2 > query.end_date):
                            objects.append(query)
                        else:
                            continue
            queryset1 = Room.objects.filter(room_number__in=[room.room_number for room in objects])
            return queryset1


class NewRoom(CreateAPIView): # work on post
    """Creates a new Room"""
    parser_classes = [FormParser, MultiPartParser, FileUploadParser, JSONParser]
    queryset = Room.objects.all()
    serializer_class = RoomSerializer


    def post(self, request, format=None):

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(data={"msg": serializer.errors}, status=status.HTTP_406_NOT_ACCEPTABLE)


class LogRoomView(CreateAPIView): # work on post
    """Creates a new Room"""
    queryset = LogRoom.objects.all()
    serializer_class = LogRoomSerializer


    def post(self, request, format=None):
        booked_date = request.data['booked_date']
        room_number = request.data['room_number']
        end_date = request.data['end_date']
        logroom = LogRoom.objects.filter(room_number=room_number)
        date_list = str(booked_date).split('-')
        date_list_end = str(end_date).split('-')
        booked_date = date(int(date_list[0]), int(date_list[1]), int(date_list[2]))
        end_date = date(int(date_list_end[0]), int(date_list_end[1]), int(date_list_end[2]))
        serializer = self.get_serializer(data=request.data)
        a = 0
        b = 0
        c = 0
        d = 0

        if len(logroom) == 0 :
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(data={"msg": serializer.errors}, status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
            for log in logroom:

                if (booked_date >= log.booked_date and booked_date <= log.end_date):
                    a+=1
                    
                
                else:
                    if (((booked_date < log.booked_date) and (end_date < log.booked_date)) or ((booked_date > log.end_date) and (end_date > log.end_date))) == True:
                        b +=1
                        
                        
            if a > 0:
                return Response({'error': "Room already booked"}, status=status.HTTP_306_RESERVED)
            elif a == 0 and b > 0:
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_300_MULTIPLE_CHOICES)
                else:
                    return Response(data={"msg": serializer.errors}, status=status.HTTP_406_NOT_ACCEPTABLE)
            elif b == 0:
                return Response({'msg':"Room already exists in log"}, status=status.HTTP_306_RESERVED)


class UpdateRoom(GenericAPIView): # work on post
    """Creates a new Room"""
    permission_classes = [IsAdminUser]
    parser_classes = [FormParser, MultiPartParser, FileUploadParser, JSONParser]
    queryset = Room.objects.all()
    serializer_class = RoomSerializer

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        else:
            return Response({"message": "failed", "details": serializer.errors})
        
    

class DetailRoom(RetrieveAPIView):
    """Detail the Room"""
    queryset = Room.objects.all()
    serializer_class = RoomSerializer

# class BookRoom(GenericAPIView):
#     #permission_classes = [IsAuthenticated]
#     queryset = Room.objects.all()
#     serializer_class = RoomSerializer
#     lookup_url_kwarg = 'pk'
#     lookup_field = 'room_number'

#     def patch(self, request, *args, **kwargs):
#         instance = self.get_object()
#         serializer = self.get_serializer(instance, data=request.data)

#         if serializer.is_valid():
#             serializer.save()
#             return Response({"message": f"Room {instance.room_number} Booked successfully"})

#         else:
#             return Response({"message": "failed", "details": serializer.errors})
        



class DeleteRoom(GenericAPIView):
    """Deletes the Room whose id has been passed through the request"""
    permission_classes = [IsAdminUser]
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    def delete(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.delete()
            return Response({
                    "info": "Object_Project deleted"
                }
            )
        except Exception as e:
            return Response({"info": e.args})
                

tasks = Task.objects.filter(verbose_name="room_data")
if len(tasks) == 0:
    LogRoomTasks(repeat=10, verbose_name="room_data")
else:
    print('Tasks aleady exists')
