from django.urls import path
from Generate_signals.consumers import (FreeCheckConsumer,
                                        PremiumCheckConsumerNew)
url_pattern = [
    path('ws/check/free', FreeCheckConsumer.as_asgi()),
    path('ws/check/premium', PremiumCheckConsumerNew.as_asgi()),

]