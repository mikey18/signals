from django.urls import path
from Generate_signals.consumers import PremiumCheckConsumer, FreeCheckConsumer
url_pattern =  [
        path('ws/check/premium', PremiumCheckConsumer.as_asgi()),
        path('ws/check/free', FreeCheckConsumer.as_asgi()),
    ]