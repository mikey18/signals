from django.apps import AppConfig
import MetaTrader5 as mt5
import atexit

class GenerateSignalsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Generate_signals'

    def ready(self):
        # Initialize MT5 when the Django server starts
        if not mt5.initialize("C:\\Program Files\\MetaTrader 5\\terminal64.exe"):
            print("MT5 initialization failed")
            raise RuntimeError("MT5 initialization failed")
        else:
            print("MT5 initialized successfully")

        # Register the MT5 shutdown function to be called on exit
        atexit.register(self.shutdown_mt5)

    def shutdown_mt5(self):
        mt5.shutdown()
        print("MT5 shutdown successfully")
