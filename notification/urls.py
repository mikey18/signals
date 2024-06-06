from django.urls import path
from .views import Register_Push_Notification

urlpatterns = [
    path('register_notification/', Register_Push_Notification.as_view()),
]
