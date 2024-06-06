from django.apps import AppConfig
from .TradeLogic.initializeMT5 import start_mt5

class GenerateSignalsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Generate_signals'

    def ready(self):
       start_mt5()
