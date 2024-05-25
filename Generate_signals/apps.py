from django.apps import AppConfig
import MetaTrader5 as mt5
import atexit
import logging
logger = logging.getLogger(__name__)

class GenerateSignalsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Generate_signals'

    def ready(self):
        # Initialize MT5 when the Django server starts
        if not mt5.initialize("C:\\Program Files\\MetaTrader 5\\terminal64.exe"):
            # print("MT5 initialization failed")
            logger.error(f"MT5 initialization failed")
            raise RuntimeError("MT5 initialization failed")
        else:
            # print("MT5 initialized successfully")
            logger.info(f"MT5 initialized successfully")
            account = 82288340
            password = 'H@W6ZaSa'
            server = 'MetaQuotes-Demo'
            login = mt5.login(login=account, password=password, server=server)

            if login:
                logger.info("Successfully logged in to demo account")
            else:
                logger.error("Failed to login to demo account")
            # Register the MT5 shutdown function to be called on exit
            atexit.register(self.shutdown_mt5)

    def shutdown_mt5(self):
        mt5.shutdown()
        print("MT5 shutdown successfully")
