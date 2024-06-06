from rest_framework import serializers
from .models import Trade_History

class Trade_HistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Trade_History
        fields = ["id", "created_at", "symbol", "stop_loss", "take_profit", "price", "type"]


