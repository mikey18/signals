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


class Premium_Trade(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.channel_layer = get_channel_layer()
        self.loop = None
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
            await self.close()

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
                # Trade is closed
                return True
        
            await self.channel_layer.group_send(
                self.room,
                {
                    'type': 'existing.trade',
                    "status": False,
                    "message": "existing trade in progress"
                }
            )
            
            await asyncio.sleep(1)  # wait for a second before checking again

    async def place_trade(self, symbol, volume, sl, tp, trade_type):
        # Define the trade request
        price = await self.get_price(self.symbol, trade_type)
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
                "type_filling": mt5.ORDER_FILLING_FOK
            }

            # Send the trade request
            result = mt5.order_send(request)
            
            # Save trade to db
            Trade_History = apps.get_model('Generate_signals', 'Trade_History')
            await database_sync_to_async(Trade_History.objects.create)(
                symbol=symbol,
                stop_loss=sl,
                take_profit=tp,
                price=price,
                type=trade_type
            )

            return result
        except Exception as e:
            print(f"place trade error {e}")

    async def place_buy_or_sell_trade(self, data):
        if await self.check_open_positions():
            return {'status': 'error', 'message': 'There is already an open trade'}

        symbol = data['symbol']
        volume = data['volume']
        sl = data['sl']
        tp = data['tp']
        condition = data['condition']

        result = await self.place_trade(symbol, volume, sl, tp, condition)

        if result.retcode != mt5.TRADE_RETCODE_DONE:
            return {'status': 'error', 'retcode': result.retcode, 'comment': result.comment}
        else:
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
                    "message": "trade placed"
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
    
    async def money_management(self):
        self.symbol = 'XAUUSD'
        risk = 0.01 
        stop_loss_pips = 250  

        # Get the initial balance
        self.initial_balance = mt5.account_info().balance

        # Calculate the amount of money to risk
        money_to_risk = self.initial_balance * risk

        # Calculate the initial lot size  and Convert to one decimal plavce with round(value, 1) 
        initial_lot_size = round((money_to_risk / stop_loss_pips), 1)

        # Define the phases and steps
        phases = {
            1: [(initial_lot_size, 250, 750), (initial_lot_size, 250, 750), (initial_lot_size, 500, 1500), (initial_lot_size, 1000, 3000)],
            2: [(2 * initial_lot_size, 250, 750), (2 * initial_lot_size, 250, 750), (2 * initial_lot_size, 500, 1500), (2 * initial_lot_size, 1000, 3000)],
            3: [(3 * initial_lot_size, 250, 750), (3 * initial_lot_size, 250, 750), (3 * initial_lot_size, 500, 1500), (3 * initial_lot_size, 1000, 3000)],
            4: [(4 * initial_lot_size, 250, 750), (4 * initial_lot_size, 250, 750), (4 * initial_lot_size, 500, 1500), (4 * initial_lot_size, 1000, 3000)]
        }

        # Set the current phase and step to zero
        current_phase = 0
        current_step = 0

        while True:
            if await self.check_open_positions():
                # await self.send(text_data=json.dumps(data))
                await self.channel_layer.group_send(
                    self.room,
                    {
                        'type': 'existing.trade',
                        'status': False,
                        "message": "existing trade in progress"
                    }
                )
                await asyncio.sleep(1)
                continue
            # Call the signal API

            signal_response = await self.get_buy_or_sell_signal()
            # signal_response = {"status": True, "condition":"BUY"}

            # If the signal is not 'buy' or 'sell', skip this iteration
            if signal_response['status'] is False:
                await asyncio.sleep(59)
                continue

            # Get the lot size, stop loss, and take profit for the current phase and step
            lot_size, stop_loss_pips, take_profit_pips = phases[current_phase + 1][current_step]

            # Get the current price
            open_price = await self.get_price(self.symbol, signal_response['condition'])
            point = mt5.symbol_info(self.symbol).point
            
            # Calculate the stop loss and take profit prices
            if signal_response['condition'] == 'BUY':
                stop_loss = await self.convert_pips_to_price(open_price, -stop_loss_pips, point)
                take_profit = await self.convert_pips_to_price(open_price, take_profit_pips, point)
            
            elif signal_response['condition'] == 'SELL':
                stop_loss = await self.convert_pips_to_price(open_price, stop_loss_pips, point)
                take_profit = await self.convert_pips_to_price(open_price, -take_profit_pips, point)

            # Define the trade request
            trade_request = {
                "symbol": self.symbol,
                "volume": lot_size,
                "sl": stop_loss,
                "tp": take_profit,
                "condition": signal_response['condition']
            }

            # Send the trade request to the appropriate API and get the trade result
            if signal_response['condition'] == 'BUY' or signal_response['condition'] == 'SELL':
                response = await self.place_buy_or_sell_trade(trade_request)

            # Check the response
            if response['status'] == 'success':
                await self.channel_layer.group_send(
                    self.room,
                    {
                        'type': 'trade.finished',
                        "status": True,
                        'data': response
                    }
                )
                # print("Trade request successful: ", response)
            else:
                await self.channel_layer.group_send(
                    self.room,
                    {
                        'type': 'existing.trade',
                        'status': False,
                        'message': "Trade request failed"
                    }
                )
                # print(f"Trade request send failed, error code: {mt5.last_error()}")
                await asyncio.sleep(59)
                continue
              
            # Check the profit or loss from the trade result
            # trade_status = response['trade_status']

            # Get the new balance from the MT5 terminal
            new_balance = mt5.account_info().balance

            if response['trade_status'] == "loss":
                # print("A loss was made.")
                # Update the current step or phase
                if current_step < 3:
                    current_step += 1
                else:
                    current_step = 0
                    if current_phase < 3:
                        current_phase += 1
                    else:
                        current_phase = 0
            elif response['trade_status'] == "profit":
                # print("A profit was made.")
                # Determine the next step based on the balance
                if new_balance > self.initial_balance:
                    # Reset the current step and phase to initial
                    current_step = 0
                    current_phase = 0
                    self.initial_balance = new_balance
                else:
                    # Remain in the same phase but reset to initial step
                    current_step = 0
    
            await self.channel_layer.group_send(
                self.room,
                {
                    'type': 'trade.finished',
                    'status': response['trade_status'],  # trade_status will be either "profit" or "loss"
                    'data': {
                        "current_phase": current_phase + 1, # int
                        "current_step": current_step, # int
                        "lot size": lot_size, # float
                        "stop loss": stop_loss, # float
                        "take profit": take_profit, # float
                        "new_account_balance": new_balance # float
                    }
                }
            )
            await asyncio.sleep(59)


    async def initiate_system(self):
        await self.money_management()

    def run(self):
        # self.loop = asyncio.new_event_loop()
        # asyncio.set_event_loop(self.loop)
        asyncio.run(self.initiate_system())