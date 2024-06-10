from django.urls import path
from .views import Seller_OrderHistoryAPI

# app_name = 'api'
urlpatterns = [
    path('history/', Seller_OrderHistoryAPI.as_view(), name='trade-signals-history'),
]
