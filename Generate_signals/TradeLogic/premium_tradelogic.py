import threading
import asyncio
from datetime import datetime, timezone
import pandas as pd
import vectorbt as vbt
import MetaTrader5 as mt5
import logging
from django.apps import apps
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from functions.notification import send_notification

logger = logging.getLogger(__name__)

# class Premium_Trade(threading.Thread):
#     def __init__(self):
#         threading.Thread.__init__(self)
#         self.channel_layer = get_channel_layer()
#         self.room = 'xauusd'

#     async def get_buy_or_sell_signal(self):
#         try:
#             # while True:
#             bars = mt5.copy_rates_from(self.symbol, mt5.TIMEFRAME_M1, datetime.now(timezone.utc), 365)
#             df = pd.DataFrame(bars)
#             df['time'] = pd.to_datetime(df['time'], unit='s')
#             df = df.set_index('time')
#             current_price = df['close'].iloc[-1]

#             # Calculate indicators
#             # print("Calculating indicators in progress...")
#             ma14 = vbt.MA.run(df['close'], 14)
#             ma50 = vbt.MA.run(df['close'], 50)
#             ma365 = vbt.MA.run(df['close'], 365)
#             rsi = vbt.RSI.run(df['close'], 14)
            
#             # Check the conditions for the last bar
#             # print("Checking conditions in progress...\n")
#             if (not (ma14.ma.iloc[-1] > ma50.ma.iloc[-1] > ma365.ma.iloc[-1] and rsi.rsi.iloc[-1] < 40)
#             and not (ma14.ma.iloc[-1] < ma50.ma.iloc[-1] < ma365.ma.iloc[-1] and rsi.rsi.iloc[-1] > 59)):
#                 print("checking for signal")

#                 data = {
#                     'status': False,
#                     'message': "checking for signal..."
#                 }
#                 await self.channel_layer.group_send(
#                     self.room,
#                     {
#                         'type': 'existing.trade',
#                         **data
#                     }
#                 )
#                 return data

#             elif (ma14.ma.iloc[-1] > ma50.ma.iloc[-1] > ma365.ma.iloc[-1] and rsi.rsi.iloc[-1] < 40):
#                 print("buy signal found")

#                 data = {
#                     'status': True,
#                     'condition':'BUY',
#                     'RSI':rsi.rsi.iloc[-1],
#                     '14 SMA': ma14.ma.iloc[-1],
#                     'Current Price': current_price
#                 }
#                 await self.channel_layer.group_send(
#                     self.room,
#                     {
#                         'type': 'existing.trade',
#                         'status': True,
#                         'message':'BUY',
#                     }
#                 )
#                 return data
            
#             elif (ma14.ma.iloc[-1] < ma50.ma.iloc[-1] < ma365.ma.iloc[-1] and rsi.rsi.iloc[-1] > 59):
#                 print("sell signal found")

#                 data = {
#                     'status': True,
#                     'condition':'SELL',
#                     'RSI':rsi.rsi.iloc[-1],
#                     '14 SMA': ma14.ma.iloc[-1],
#                     'Current Price': current_price
#                 }
#                 await self.channel_layer.group_send(
#                     self.room,
#                     {
#                         'type': 'existing.trade',
#                         'status': True,
#                         'message':'SELL',
#                     }
#                 )             
#                 return data
#             # await asyncio.sleep(59)  # wait for 59 seconds
#         except Exception as e:
#             logger.error(f"Error in WebSocket task: {e}")

#     async def check_profit_or_loss(self, initial_balance):
#         # Get the new balance from the MT5 terminal
#         account_info = mt5.account_info()
#         new_balance = account_info.balance

#         if initial_balance < new_balance:
#             return "profit"
#         elif initial_balance > new_balance:
#             return "loss"
#         else:
#             return "no change"

#     async def check_open_positions(self):
#         # Get the open positions from MT5
#         positions = mt5.positions_get()
#         return len(positions) > 0
    
#     async def wait_for_trade_close(self, order_id):
#         while True:
#             # Get all active orders
#             positions = mt5.positions_get(ticket=order_id)
#             if not positions:
#                 return True
            
#             print('trade in progress')
#             last_position = await self.get_last_position()
#             await self.channel_layer.group_send(
#                 self.room,
#                 {
#                     'type': 'trade.finished',
#                     'status': True,
#                     "message": "active trade in progress",
#                     "data": {
#                         "symbol": last_position.symbol,
#                         "trade_type": 'BUY' if last_position.type == 0 else 'SELL',
#                         "stop_loss": last_position.sl,
#                         "take_profit": last_position.tp,
#                         "open_price": last_position.price_open,
#                         "curent_price": last_position.price_current
#                     }
#                 }
#             )
#             await asyncio.sleep(1)  # wait for a second before checking again

#     async def place_trade(self, symbol, volume, sl, tp, trade_type, price):
#         # Define the trade request
#         try:
#             request = {
#                 "action": mt5.TRADE_ACTION_DEAL,
#                 "symbol": symbol,
#                 "volume": volume,
#                 "sl": sl,
#                 "tp": tp,
#                 "price": price,
#                 "deviation": 10,
#                 "magic": 123456,
#                 "type": mt5.ORDER_TYPE_BUY if trade_type == 'BUY' else mt5.ORDER_TYPE_SELL,
#                 "type_filling": mt5.ORDER_FILLING_FOK,
#                 "comment": f'signal.{self.current_phase}.{self.current_step}'
#             }

#             # Send the trade request
#             result = mt5.order_send(request)        
#             return result
#         except Exception as e:
#             logger.error(f"place trade error: {e}")
#             # print(f"place trade error {e}")

#     async def place_buy_or_sell_trade(self, data):
#         if await self.check_open_positions():
#             return {'status': 'error', 'message': 'There is already an open trade'}

#         symbol = data['symbol']
#         volume = data['volume']
#         sl = data['sl']
#         tp = data['tp']
#         condition = data['condition']
#         price=data['price']

#         result = await self.place_trade(symbol, volume, sl, tp, condition, price)

#         if result.retcode != mt5.TRADE_RETCODE_DONE:
#             return {'status': 'error', 'retcode': result.retcode, 'comment': result.comment}
#         else:
#             print("trade placed")
#             # send notification
#             asyncio.create_task(send_notification(
#                 title="Trade placed",
#                 body="A signal was received and trade has been placed"
#             ))
#             # send notification
            
#             await self.channel_layer.group_send(
#                 self.room,
#                 {
#                     'type': 'existing.trade',
#                     "status": True,
#                     "message": "A signal was received and trade has been placed"
#                 }
#             )
#             closed_trade = await self.wait_for_trade_close(result.order)
#             if closed_trade:
#                 trade_status = await self.check_profit_or_loss(self.initial_balance)
#                 return {'status': 'success', 'order': result.order, 'retcode': result.retcode, 'trade_status': trade_status}
    
#     async def get_price(self, symbol, trade_type):
#         tick_info = mt5.symbol_info_tick(symbol)
#         price = tick_info.ask if trade_type == 'BUY' else tick_info.bid
#         return price

#     async def convert_pips_to_price(self, price, pips, point):
#         return price + (pips * point)
    
#     async def has_more_than_two_decimal_places(self, value):
#         # Convert the value to a string to check the number of decimal places
#         str_value = str(value)
        
#         # Check if the value has a decimal point
#         if '.' in str_value:
#             # Split the string into the integer and decimal parts
#             parts = str_value.split('.')
#             # Check if the decimal part has more than two digits
#             return len(parts[1]) > 2
#         return False

#     async def convert_to_two_decimal_places(self, value):
#         if await self.has_more_than_two_decimal_places(value):
#             # Use round() to round the value to two decimal places
#             value = round(value, 2)
#         return value
    
#     async def get_last_position(self):
#         positions = mt5.positions_get()
#         filtered_positions = [position for position in positions if position.comment.lower().startswith('signal')]
#         if filtered_positions:
#             last_position = filtered_positions[-1]
#             return last_position
#         return False
    
#     async def save_to_db(self, symbol, stop_loss, take_profit, open_price, trade_type, initial_balance):
#         Trade_History = apps.get_model('Generate_signals', 'Trade_History')
#         await database_sync_to_async(Trade_History.objects.create)(
#             symbol=symbol,
#             stop_loss=stop_loss,
#             take_profit=take_profit,
#             price=open_price,
#             type=trade_type,
#             result=initial_balance
#         )

#     async def adjust_phases_and_steps(self, trade_status):
#         # Check the profit or loss from the trade result
#         # Get the new balance from the MT5 terminal
#         new_balance = mt5.account_info().balance
#         if trade_status == "loss":
#             # print("A loss was made.")
#             # Update the current step or phase
#             if self.current_step < 3:
#                 self.current_step += 1
#             else:
#                 self.current_step = 0
#                 if self.current_phase < 3:
#                     self.current_phase += 1
#                 else:
#                     self.current_phase = 0
#         elif trade_status == "profit":
#             # print("A profit was made.")
#             # Determine the next step based on the balance
#             if new_balance > self.initial_balance:
#                 # Reset the current step and phase to initial
#                 self.current_step = 0
#                 self.current_phase = 0
#                 self.initial_balance = new_balance
#             else:
#                 # Remain in the same phase but reset to initial step
#                 self.current_step = 0

#     async def money_management(self):
#         self.symbol = 'XAUUSD'
#         risk = 0.01 
#         stop_loss_pips = 250  
#         # Get the initial balance
#         self.initial_balance = mt5.account_info().balance
#         # Calculate the amount of money to risk
#         money_to_risk = self.initial_balance * risk
#         # Calculate the initial lot size  and Convert to one decimal plavce with round(value, 1) 
#         if type(money_to_risk) is int:
#             initial_lot_size = round((money_to_risk / stop_loss_pips), 1)
#         elif type(money_to_risk) is float:
#             calculation = money_to_risk / stop_loss_pips
#             initial_lot_size = await self.convert_to_two_decimal_places(calculation)

#         # Define the phases and steps
#         phases = {
#             1: [(initial_lot_size, 250, 750), (initial_lot_size, 250, 750), (initial_lot_size, 500, 1500), (initial_lot_size, 1000, 3000)],
#             2: [(2 * initial_lot_size, 250, 750), (2 * initial_lot_size, 250, 750), (2 * initial_lot_size, 500, 1500), (2 * initial_lot_size, 1000, 3000)],
#             3: [(3 * initial_lot_size, 250, 750), (3 * initial_lot_size, 250, 750), (3 * initial_lot_size, 500, 1500), (3 * initial_lot_size, 1000, 3000)],
#             4: [(4 * initial_lot_size, 250, 750), (4 * initial_lot_size, 250, 750), (4 * initial_lot_size, 500, 1500), (4 * initial_lot_size, 1000, 3000)]
#         }

#         # Set the current phase and step to zero
#         self.current_phase = 0
#         self.current_step = 0
        
#         trade_was_active = False
#         while True:
#             if await self.check_open_positions():
#                 trade_was_active = True
#                 trade_data = None
#                 print('trade in progress 0')
#                 last_position = await self.get_last_position()
#                 trade_data = {
#                     "symbol": last_position.symbol,
#                     "trade_type": 'BUY' if last_position.type == 0 else 'SELL',
#                     "stop_loss": last_position.sl,
#                     "take_profit": last_position.tp,
#                     "open_price": last_position.price_open,
#                     "lot_size": last_position.volume
#                 }
#                 await self.channel_layer.group_send(
#                     self.room,
#                     {
#                         'type': 'trade.finished',
#                         'status': True,
#                         "message": "active trade in progress",
#                         "data": {
#                             **trade_data,
#                             "curent_price": last_position.price_current
#                         }
#                     }
#                 )
#                 await asyncio.sleep(1)
#                 continue
            
#             # Checks if active trade was from signal server
#             if trade_was_active:
#                 await self.channel_layer.group_send(
#                     self.room,
#                     {
#                         'type': 'trade.finished',
#                         'status': True,
#                         'message': 'Trade completed',
#                         'data': {
#                             "result": await self.check_profit_or_loss(self.initial_balance),  # trade_status will be either "profit" or "loss"
#                             "current_phase": self.current_phase + 1, # int
#                             "current_step": self.current_step, # int
#                             "lot_size": trade_data['lot_size'], # float
#                             "stop_loss": trade_data['stop_loss'], # float
#                             "take_profit": trade_data['take_profit'], # float
#                             "new_account_balance": mt5.account_info().balance # float
#                         }
#                     }
#                 )
#                 if last_position.comment.lower().startswith('signal'):
#                     # Save trade to db
#                     print('saving to db')
#                     trade_status = await self.check_profit_or_loss(self.initial_balance)
#                     Trade_History = apps.get_model('Generate_signals', 'Trade_History')
#                     await self.save_to_db(trade_data['symbol'], 
#                                           trade_data['stop_loss'],
#                                           trade_data['take_profit'],
#                                           trade_data['open_price'],
#                                           trade_data['trade_type'],
#                                           trade_status)
#                     # Save trade to db
#                     trade_was_active = False
#                     trade_data = None

#                     parts = last_position.comment.lower().split(".")
#                     self.current_phase = int(parts[1])
#                     self.current_step = int(parts[2])

#                     # adjust phases and steps
#                     await self.adjust_phases_and_steps(trade_status)
#                     # adjust phases and steps

#             # Checks if active trade was from signal server
#             # Call the signal API

#             signal_response = await self.get_buy_or_sell_signal()
#             # signal_response = {"status": True, "condition":"BUY"}

#             # If the signal is not 'buy' or 'sell', skip this iteration
#             if signal_response['status'] is False:
#                 await asyncio.sleep(59)
#                 continue
         
#             # Get the lot size, stop loss, and take profit for the current phase and step
#             lot_size, stop_loss_pips, take_profit_pips = phases[self.current_phase + 1][self.current_step]

#             # Get the current price
#             price = await self.get_price(self.symbol, signal_response['condition'])
#             point = mt5.symbol_info(self.symbol).point
            
#             # Calculate the stop loss and take profit prices
#             multiplier = 1 if signal_response['condition'] == 'BUY' else -1
#             stop_loss = await self.convert_pips_to_price(price, multiplier * -stop_loss_pips, point)
#             take_profit = await self.convert_pips_to_price(price, multiplier * take_profit_pips, point)
            

#             # Define the trade request
#             trade_request = {
#                 "symbol": self.symbol,
#                 "volume": lot_size,
#                 "sl": stop_loss,
#                 "tp": take_profit,
#                 "condition": signal_response['condition'],
#                 "price": price
#             }

#             # Send the trade request to the appropriate API and get the trade result
#             if signal_response['condition'] == 'BUY' or signal_response['condition'] == 'SELL':
#                 response = await self.place_buy_or_sell_trade(trade_request)

#             # Check the response
#             if response['status'] == 'success':
#                 # Save trade to db
#                 print('saving to db')
#                 Trade_History = apps.get_model('Generate_signals', 'Trade_History')
#                 await database_sync_to_async(Trade_History.objects.create)(
#                     symbol=self.symbol,
#                     stop_loss=stop_loss,
#                     take_profit=take_profit,
#                     price=price,
#                     type=signal_response['condition'],
#                     result=response['trade_status']
#                 )
#                 await self.save_to_db(self.symbol, 
#                                         stop_loss,
#                                         take_profit,
#                                         price,
#                                         signal_response['condition'],
#                                         response['trade_status'])
#                 # Save trade to db
#             else:
#                 print("trade couldn't place")
#                 await self.channel_layer.group_send(
#                     self.room,
#                     {
#                         'type': 'existing.trade',
#                         'status': False,
#                         'message': "Trade request failed"
#                     }
#                 )
#                 await asyncio.sleep(59)
#                 continue
           
#             # adjust phases and steps
#             await self.adjust_phases_and_steps(response['trade_status'])
#             # adjust phases and steps

#             await self.channel_layer.group_send(
#                 self.room,
#                 {
#                     'type': 'trade.finished',
#                     'status': True,
#                     'message': 'Trade completed',
#                     'data': {
#                         "result": response['trade_status'],  # trade_status will be either "profit" or "loss"
#                         "current_phase": self.current_phase + 1, # int
#                         "current_step": self.current_step, # int
#                         "lot_size": lot_size, # float
#                         "stop_loss": stop_loss, # float
#                         "take_profit": take_profit, # float
#                         "new_account_balance": mt5.account_info().balance # float
#                     }
#                 }
#             )
#             await asyncio.sleep(59)

#     async def initiate_system(self):
#         await self.money_management()

#     def run(self):
#         # self.loop = asyncio.new_event_loop()
#         # asyncio.set_event_loop(self.loop)
#         asyncio.run(self.initiate_system())



class Premium_Trade:
    def __init__(self):
        self.channel_layer = get_channel_layer()
        self.room = 'xauusd'

    async def get_buy_or_sell_signal(self):
        try:
            # while True:
            bars = mt5.copy_rates_from(self.symbol, mt5.TIMEFRAME_M1, datetime.now(timezone.utc), 365)
            df = pd.DataFrame(bars)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            df = df.set_index('time')
            current_price = df['close'].iloc[-1]

            # Calculate indicators
            # print("Calculating indicators in progress...")
            ma14 = vbt.MA.run(df['close'], 14)
            ma50 = vbt.MA.run(df['close'], 50)
            ma365 = vbt.MA.run(df['close'], 365)
            rsi = vbt.RSI.run(df['close'], 14)
            
            # Check the conditions for the last bar
            # print("Checking conditions in progress...\n")
            if (not (ma14.ma.iloc[-1] > ma50.ma.iloc[-1] > ma365.ma.iloc[-1] and rsi.rsi.iloc[-1] < 40)
            and not (ma14.ma.iloc[-1] < ma50.ma.iloc[-1] < ma365.ma.iloc[-1] and rsi.rsi.iloc[-1] > 59)):
                print("checking for signal")

                data = {
                    'status': False,
                    'message': "checking for signal..."
                }
                await self.channel_layer.group_send(
                    self.room,
                    {
                        'type': 'existing.trade',
                        **data
                    }
                )
                return data

            elif (ma14.ma.iloc[-1] > ma50.ma.iloc[-1] > ma365.ma.iloc[-1] and rsi.rsi.iloc[-1] < 40):
                print("buy signal found")

                data = {
                    'status': True,
                    'condition':'BUY',
                    'RSI':rsi.rsi.iloc[-1],
                    '14 SMA': ma14.ma.iloc[-1],
                    'Current Price': current_price
                }
                await self.channel_layer.group_send(
                    self.room,
                    {
                        'type': 'existing.trade',
                        'status': True,
                        'message':'BUY',
                    }
                )
                return data
            
            elif (ma14.ma.iloc[-1] < ma50.ma.iloc[-1] < ma365.ma.iloc[-1] and rsi.rsi.iloc[-1] > 59):
                print("sell signal found")

                data = {
                    'status': True,
                    'condition':'SELL',
                    'RSI':rsi.rsi.iloc[-1],
                    '14 SMA': ma14.ma.iloc[-1],
                    'Current Price': current_price
                }
                await self.channel_layer.group_send(
                    self.room,
                    {
                        'type': 'existing.trade',
                        'status': True,
                        'message':'SELL',
                    }
                )             
                return data
            # await asyncio.sleep(59)  # wait for 59 seconds
        except Exception as e:
            logger.error(f"Error in WebSocket task: {e}")

    async def check_profit_or_loss(self, initial_balance):
        # Get the new balance from the MT5 terminal
        account_info = mt5.account_info()
        new_balance = account_info.balance

        if initial_balance < new_balance:
            return "profit"
        elif initial_balance > new_balance:
            return "loss"
        else:
            return "no change"

    async def check_open_positions(self):
        # Get the open positions from MT5
        positions = mt5.positions_get()
        return len(positions) > 0
    
    async def wait_for_trade_close(self, order_id):
        while True:
            # Get all active orders
            positions = mt5.positions_get(ticket=order_id)
            if not positions:
                return True
            
            print('trade in progress')
            last_position = await self.get_last_position()
            await self.channel_layer.group_send(
                self.room,
                {
                    'type': 'trade.finished',
                    'status': True,
                    "message": "active trade in progress",
                    "data": {
                        "symbol": last_position.symbol,
                        "trade_type": 'BUY' if last_position.type == 0 else 'SELL',
                        "stop_loss": last_position.sl,
                        "take_profit": last_position.tp,
                        "open_price": last_position.price_open,
                        "curent_price": last_position.price_current
                    }
                }
            )
            await asyncio.sleep(1)  # wait for a second before checking again

    async def place_trade(self, symbol, volume, sl, tp, trade_type, price):
        # Define the trade request
        try:
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": volume,
                "sl": sl,
                "tp": tp,
                "price": price,
                "deviation": 10,
                "magic": 123456,
                "type": mt5.ORDER_TYPE_BUY if trade_type == 'BUY' else mt5.ORDER_TYPE_SELL,
                "type_filling": mt5.ORDER_FILLING_FOK,
                "comment": f'signal.{self.current_phase}.{self.current_step}'
            }

            # Send the trade request
            result = mt5.order_send(request)        
            return result
        except Exception as e:
            logger.error(f"place trade error: {e}")
            # print(f"place trade error {e}")

    async def place_buy_or_sell_trade(self, data):
        if await self.check_open_positions():
            return {'status': 'error', 'message': 'There is already an open trade'}

        symbol = data['symbol']
        volume = data['volume']
        sl = data['sl']
        tp = data['tp']
        condition = data['condition']
        price=data['price']

        result = await self.place_trade(symbol, volume, sl, tp, condition, price)

        if result.retcode != mt5.TRADE_RETCODE_DONE:
            return {'status': 'error', 'retcode': result.retcode, 'comment': result.comment}
        else:
            print("trade placed")
            # send notification
            asyncio.create_task(send_notification(
                title="Trade placed",
                body="A signal was received and trade has been placed"
            ))
            # send notification
            
            await self.channel_layer.group_send(
                self.room,
                {
                    'type': 'existing.trade',
                    "status": True,
                    "message": "A signal was received and trade has been placed"
                }
            )
            closed_trade = await self.wait_for_trade_close(result.order)
            if closed_trade:
                trade_status = await self.check_profit_or_loss(self.initial_balance)
                return {'status': 'success', 'order': result.order, 'retcode': result.retcode, 'trade_status': trade_status}
    
    async def get_price(self, symbol, trade_type):
        tick_info = mt5.symbol_info_tick(symbol)
        price = tick_info.ask if trade_type == 'BUY' else tick_info.bid
        return price

    async def convert_pips_to_price(self, price, pips, point):
        return price + (pips * point)
    
    async def convert_to_two_decimal_places(self, value):
        async def has_more_than_two_decimal_places(value):
            # Convert the value to a string to check the number of decimal places
            str_value = str(value)
            
            # Check if the value has a decimal point
            if '.' in str_value:
                # Split the string into the integer and decimal parts
                parts = str_value.split('.')
                # Check if the decimal part has more than two digits
                return len(parts[1]) > 2
            return False
        
        if await has_more_than_two_decimal_places(value):
            # Use round() to round the value to two decimal places
            value = round(value, 2)
        return value
    
    async def get_last_position(self):
        positions = mt5.positions_get()
        filtered_positions = [position for position in positions if position.comment.lower().startswith('signal')]
        if filtered_positions:
            last_position = filtered_positions[-1]
            return last_position
        return False
    
    async def save_to_db(self, symbol, stop_loss, take_profit, open_price, trade_type, initial_balance):
        Trade_History = apps.get_model('Generate_signals', 'Trade_History')
        await database_sync_to_async(Trade_History.objects.create)(
            symbol=symbol,
            stop_loss=stop_loss,
            take_profit=take_profit,
            price=open_price,
            type=trade_type,
            result=initial_balance
        )

    async def adjust_phases_and_steps(self, trade_status):
        # Check the profit or loss from the trade result
        # Get the new balance from the MT5 terminal
        new_balance = mt5.account_info().balance
        if trade_status == "loss":
            # print("A loss was made.")
            # Update the current step or phase
            if self.current_step < 3:
                self.current_step += 1
            else:
                self.current_step = 0
                if self.current_phase < 3:
                    self.current_phase += 1
                else:
                    self.current_phase = 0
        elif trade_status == "profit":
            # print("A profit was made.")
            # Determine the next step based on the balance
            if new_balance > self.initial_balance:
                # Reset the current step and phase to initial
                self.current_step = 0
                self.current_phase = 0
                self.initial_balance = new_balance
            else:
                # Remain in the same phase but reset to initial step
                self.current_step = 0

    async def money_management(self):
        self.symbol = 'XAUUSD'
        risk = 0.001 
        stop_loss_pips = 250  
        # Get the initial balance
        self.initial_balance = mt5.account_info().balance
        # Calculate the amount of money to risk
        money_to_risk = self.initial_balance * risk
        # Calculate the initial lot size  and Convert to one decimal plavce with round(value, 1) 
        if type(money_to_risk) is int:
            initial_lot_size = round((money_to_risk / stop_loss_pips), 1)
        elif type(money_to_risk) is float:
            calculation = money_to_risk / stop_loss_pips
            if calculation < 0.01:
                initial_lot_size = 0.01
            else:
                initial_lot_size = await self.convert_to_two_decimal_places(calculation)

        # Define the phases and steps
        phases = {
            1: [(initial_lot_size, 250, 750), (initial_lot_size, 250, 750), (initial_lot_size, 500, 1500), (initial_lot_size, 1000, 3000)],
            2: [(2 * initial_lot_size, 250, 750), (2 * initial_lot_size, 250, 750), (2 * initial_lot_size, 500, 1500), (2 * initial_lot_size, 1000, 3000)],
            3: [(3 * initial_lot_size, 250, 750), (3 * initial_lot_size, 250, 750), (3 * initial_lot_size, 500, 1500), (3 * initial_lot_size, 1000, 3000)],
            4: [(4 * initial_lot_size, 250, 750), (4 * initial_lot_size, 250, 750), (4 * initial_lot_size, 500, 1500), (4 * initial_lot_size, 1000, 3000)]
        }

        # Set the current phase and step to zero
        self.current_phase = 0
        self.current_step = 0
        
        trade_was_active = False
        while True:
            if await self.check_open_positions():
                trade_was_active = True
                trade_data = None
                print('trade in progress 0')
                last_position = await self.get_last_position()
                trade_data = {
                    "symbol": last_position.symbol,
                    "trade_type": 'BUY' if last_position.type == 0 else 'SELL',
                    "stop_loss": last_position.sl,
                    "take_profit": last_position.tp,
                    "open_price": last_position.price_open,
                    "lot_size": last_position.volume
                }
                await self.channel_layer.group_send(
                    self.room,
                    {
                        'type': 'trade.finished',
                        'status': True,
                        "message": "active trade in progress",
                        "data": {
                            **trade_data,
                            "curent_price": last_position.price_current
                        }
                    }
                )
                await asyncio.sleep(1)
                continue
            
            # Checks if active trade was from signal server
            if trade_was_active:
                await self.channel_layer.group_send(
                    self.room,
                    {
                        'type': 'trade.finished',
                        'status': True,
                        'message': 'Trade completed',
                        'data': {
                            "result": await self.check_profit_or_loss(self.initial_balance),  # trade_status will be either "profit" or "loss"
                            "trade_type": trade_data['trade_type'],
                            "current_phase": self.current_phase + 1, # int
                            "current_step": self.current_step, # int
                            "lot_size": trade_data['lot_size'], # float
                            "stop_loss": trade_data['stop_loss'], # float
                            "take_profit": trade_data['take_profit'], # float
                            "new_account_balance": mt5.account_info().balance # float
                        }
                    }
                )
                if last_position.comment.lower().startswith('signal'):
                    # Save trade to db
                    print('saving to db')
                    trade_status = await self.check_profit_or_loss(self.initial_balance)
                    Trade_History = apps.get_model('Generate_signals', 'Trade_History')
                    await self.save_to_db(trade_data['symbol'], 
                                          trade_data['stop_loss'],
                                          trade_data['take_profit'],
                                          trade_data['open_price'],
                                          trade_data['trade_type'],
                                          trade_status)
                    # Save trade to db
                    trade_was_active = False
                    trade_data = None

                    parts = last_position.comment.lower().split(".")
                    self.current_phase = int(parts[1])
                    self.current_step = int(parts[2])

                    # adjust phases and steps
                    await self.adjust_phases_and_steps(trade_status)
                    # adjust phases and steps

            # Checks if active trade was from signal server
            # Call the signal API

            signal_response = await self.get_buy_or_sell_signal()
            # signal_response = {"status": True, "condition":"BUY"}

            # If the signal is not 'buy' or 'sell', skip this iteration
            if signal_response['status'] is False:
                await asyncio.sleep(59)
                continue
         
            # Get the lot size, stop loss, and take profit for the current phase and step
            lot_size, stop_loss_pips, take_profit_pips = phases[self.current_phase + 1][self.current_step]

            # Get the current price
            price = await self.get_price(self.symbol, signal_response['condition'])
            point = mt5.symbol_info(self.symbol).point
            
            # Calculate the stop loss and take profit prices
            multiplier = 1 if signal_response['condition'] == 'BUY' else -1
            stop_loss = await self.convert_pips_to_price(price, multiplier * -stop_loss_pips, point)
            take_profit = await self.convert_pips_to_price(price, multiplier * take_profit_pips, point)
            

            # Define the trade request
            trade_request = {
                "symbol": self.symbol,
                "volume": lot_size,
                "sl": stop_loss,
                "tp": take_profit,
                "condition": signal_response['condition'],
                "price": price
            }

            # Send the trade request to the appropriate API and get the trade result
            if signal_response['condition'] == 'BUY' or signal_response['condition'] == 'SELL':
                response = await self.place_buy_or_sell_trade(trade_request)

            # Check the response
            if response['status'] == 'success':
                # Save trade to db
                print('saving to db')
                Trade_History = apps.get_model('Generate_signals', 'Trade_History')
                await database_sync_to_async(Trade_History.objects.create)(
                    symbol=self.symbol,
                    stop_loss=stop_loss,
                    take_profit=take_profit,
                    price=price,
                    type=signal_response['condition'],
                    result=response['trade_status']
                )
                await self.save_to_db(self.symbol, 
                                        stop_loss,
                                        take_profit,
                                        price,
                                        signal_response['condition'],
                                        response['trade_status'])
                # Save trade to db
            else:
                print("trade couldn't place")
                await self.channel_layer.group_send(
                    self.room,
                    {
                        'type': 'existing.trade',
                        'status': False,
                        'message': "Trade request failed"
                    }
                )
                await asyncio.sleep(59)
                continue
           
            # adjust phases and steps
            await self.adjust_phases_and_steps(response['trade_status'])
            # adjust phases and steps

            await self.channel_layer.group_send(
                self.room,
                {
                    'type': 'trade.finished',
                    'status': True,
                    'message': 'Trade completed',
                    'data': {
                        "result": response['trade_status'],  # trade_status will be either "profit" or "loss"
                        "trade_type": signal_response['condition'],
                        "current_phase": self.current_phase + 1, # int
                        "current_step": self.current_step, # int
                        "lot_size": lot_size, # float
                        "stop_loss": stop_loss, # float
                        "take_profit": take_profit, # float
                        "new_account_balance": mt5.account_info().balance # float
                    }
                }
            )
            await asyncio.sleep(59)

    def initiate_system(self):
        asyncio.run(self.money_management())