from django.urls import path
from .views import (Users)
from . import views
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

urlpatterns = [
    path('users/', Users.as_view(), name="all-admin"),
    path('register/',views.RegisterView.as_view(),name="register"),
    path('login/',views.LoginAPIView.as_view(),name="login"),
    path('logout/', views.LogoutAPIView.as_view(), name="logout"),
    #path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]