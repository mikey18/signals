from django.urls import path
from . import views

urlpatterns = [
    path('register/',views.RegisterView.as_view(),name="register"),
    path('login/',views.LoginAPIView.as_view(),name="login"),
    path('logout/', views.LogoutAPIView.as_view(), name="logout"),
    # path('sse/', views.SSE.as_view(), name="SSE"),
]