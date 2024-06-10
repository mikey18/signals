from celery import shared_task
from .TradeLogic.premium_tradelogic import Premium_Trade

@shared_task
def run_my_task_class_method():
    classs = Premium_Trade()
    classs.initiate_system()


