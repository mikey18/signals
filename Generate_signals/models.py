from django.db import models

class Trade_History(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    symbol = models.CharField(max_length=100)
    stop_loss = models.FloatField()
    take_profit = models.FloatField()
    price = models.FloatField()
    type = models.CharField(max_length=100)

    def __str__(self):
        return str(self.id)
    


