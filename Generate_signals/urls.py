from .views import AllRoom, NewRoom, DeleteRoom, DetailRoom, UpdateRoom, LogRoomView
from django.urls import path, re_path

# app_name = 'api'

urlpatterns = [
    path('room/add/', NewRoom.as_view(), name='new-room'),
    path('room/all/', AllRoom.as_view(), name='all-room'),
    path('room/log/', LogRoomView.as_view(), name='log-room'),
    path('room/update/<str:pk>', UpdateRoom.as_view(), name='update-room'),
    path('room/detailed/<str:pk>/', DetailRoom.as_view(), name='detail-room'),
    path('room/delete/<str:pk>', DeleteRoom.as_view(), name='delete-room'),
    #path('room/book_room/<int:pk>', BookRoom.as_view(), name='book-room'),
]
