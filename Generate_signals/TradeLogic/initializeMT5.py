import MetaTrader5 as mt5
import atexit
import logging
# from .premium_tradelogic import Premium_Trade
from ..tasks import run_my_task_class_method
logger = logging.getLogger(__name__)

def shutdown_mt5():
    mt5.shutdown()
    print("MT5 shutdown successfully")

def start_mt5():
    # Initialize MT5 when the Django server starts
    if not mt5.initialize("C:\\Program Files\\MetaTrader 5\\terminal64.exe"):
        # print("MT5 initialization failed")
        logger.error(f"MT5 initialization failed")
        raise RuntimeError("MT5 initialization failed")
    else:
        # print("MT5 initialized successfully")
        logger.info(f"MT5 initialized successfully")
        account = 10003376634
        password = '3t+xAuQi'
        server = 'MetaQuotes-Demo'
        login = mt5.login(login=account, password=password, server=server)

        if login:
            logger.info("Successfully logged in to demo account")
        else:
            logger.error("Failed to login to demo account")
        # Register the MT5 shutdown function to be called on exit
        atexit.register(shutdown_mt5)
        
        # thread = Premium_Trade()
        # thread.daemon = True
        # thread.start()
        run_my_task_class_method.delay()


  