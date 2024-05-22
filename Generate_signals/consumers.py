import pandas as pd
import vectorbt as vbt
import datetime
import MetaTrader5 as mt5
import json
from channels.generic.websocket import AsyncWebsocketConsumer
import asyncio

class PremiumCheckConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        self.send_task = False
        self.task_running = False

    async def disconnect(self, message):
        if self.send_task:
            self.send_task.cancel()
        await self.close()

    async def receive(self, text_data):
        try:
            client_data = json.loads(text_data)
            self.symbol = 'XAUUSD'
            if client_data["msg"] == "ping" and self.task_running == False:
                self.task_running = True
                self.send_task = asyncio.create_task(self.get_buy_or_sell_signal())

            elif client_data["msg"] != "ping" and self.task_running:
                await self.send(text_data=json.dumps({'status': False}))

            elif client_data["msg"] != "ping":
                await self.send(text_data=json.dumps({'message': f"error"}))
                await self.close()
        except Exception:
            await self.close()

    async def get_buy_or_sell_signal(self):
        while True:
            print("Getting data in progress...")
            # Get the latest data
            bars = mt5.copy_rates_from(self.symbol, mt5.TIMEFRAME_M1, datetime.datetime.now(), 365)
            df = pd.DataFrame(bars)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            df = df.set_index('time')
            current_price = df['close'].iloc[-1]

            # Calculate indicators
            print("Calculating indicators in progress...")
            ma14 = vbt.MA.run(df['close'], 14)
            ma50 = vbt.MA.run(df['close'], 50)
            ma365 = vbt.MA.run(df['close'], 365)
            rsi = vbt.RSI.run(df['close'], 14)
            
            # Check the conditions for the last bar
            print("Checking conditions in progress...\n")
            if (not (ma14.ma.iloc[-1] > ma50.ma.iloc[-1] > ma365.ma.iloc[-1] and rsi.rsi.iloc[-1] < 40)
            and not (ma14.ma.iloc[-1] < ma50.ma.iloc[-1] < ma365.ma.iloc[-1] and rsi.rsi.iloc[-1] > 60)):
                await self.send(text_data=json.dumps({
                    'status': False,
                    'message': "polling"
                }))

            if (ma14.ma.iloc[-1] > ma50.ma.iloc[-1] > ma365.ma.iloc[-1] and rsi.rsi.iloc[-1] < 40):
                await self.send(text_data=json.dumps({
                                'status': True,
                                'condition':'BUY',
                                'RSI':rsi.rsi.iloc[-1],
                                '14 SMA': ma14.ma.iloc[-1],
                                'Current Price': current_price
                                }))
                print("Buy condition met:")
                print(f"RSI: {rsi.rsi.iloc[-1]:.2f} (below 40)")
                print(f"14 SMA: {ma14.ma.iloc[-1]:.5f} (above 50 SMA and 50 SMA > 365 SMA)")
                print(f"Current price: {current_price:.5f}")
                print("-" * 30)
            
            elif (ma14.ma.iloc[-1] < ma50.ma.iloc[-1] < ma365.ma.iloc[-1] and rsi.rsi.iloc[-1] > 60):
                await self.send(text_data=json.dumps({
                                            'status': True,
                                            'condition':'SELL',
                                            'RSI':rsi.rsi.iloc[-1],
                                            '14 SMA': ma14.ma.iloc[-1],
                                            'Current Price': current_price
                                            }))
                print("Sell condition met:")
                print(f"RSI: {rsi.rsi.iloc[-1]:.2f} (above 60)")
                print(f"14 SMA: {ma14.ma.iloc[-1]:.5f} (below 50 SMA and 50 SMA < 365 SMA)")
                print(f"Current price: {current_price:.5f}")
                print("-" * 30)
            await asyncio.sleep(2)  # wait for 60 seconds

class FreeCheckConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        if not mt5.initialize("C:\\Program Files\\MetaTrader 5\\terminal64.exe"):
            print("MT5 initialization failed")
            await self.send(text_data=json.dumps({
                'message': "failed to load mt5"
            }))
        
        await self.send(text_data=json.dumps({
            'message': "started"
        }))
        self.send_task = False
        self.task_running = False

    async def disconnect(self, message):
        if self.send_task:
            self.send_task.cancel()
        await self.close()

    async def receive(self, text_data):
        try:
            client_data = json.loads(text_data)
            self.symbol = 'XAUUSD'  # or any other valid symbol
            if client_data["msg"] == "ping" and self.task_running == False:
                self.task_running = True
                self.send_task = asyncio.create_task(self.get_buy_or_sell_signal())

            elif client_data["msg"] != "ping" and self.task_running:
                await self.send(text_data=json.dumps({'status': False}))

            elif client_data["msg"] != "ping":
                await self.send(text_data=json.dumps({'message': f"error"}))
                await self.close()
        except Exception:
            await self.close()

    async def get_buy_or_sell_signal(self):
        try:
            while True:
                symbol_info = mt5.symbol_info(self.symbol)
                print("Getting data in progress...")
                # Get the latest data
                bars = mt5.copy_rates_from(self.symbol, mt5.TIMEFRAME_M1, datetime.datetime.now(), 365)
                df = pd.DataFrame(bars)
                df['time'] = pd.to_datetime(df['time'], unit='s')
                df = df.set_index('time')
                # Calculate RSI
                rsi = vbt.RSI.run(df['close'], 14)
                # Check buy condition
                buy_condition = rsi.rsi > 78
                # Check sell condition
                sell_condition = rsi.rsi < 22
                if not buy_condition.iloc[-1] and not sell_condition.iloc[-1]:
                    await self.send(text_data=json.dumps({
                        'status': False,
                        'message': "polling"
                    }))

                if buy_condition.iloc[-1]:
                    print("Buy condition met:")
                    current_price = df['close'].iloc[-1]
                    stop_loss = current_price - 1000 * symbol_info.point
                    take_profit = current_price + 1500* symbol_info.point
                    await self.send(text_data=json.dumps({
                                                'status': True,
                                                'condition':'BUY',
                                                'RSI':rsi.rsi.iloc[-1],
                                                'Current Price': current_price,
                                                'SL': stop_loss,
                                                'TP': take_profit
                                                }))
                    print(f"RSI: {rsi.rsi.iloc[-1]:.2f} (above 78)")
                    print(f"Current price: {current_price:.5f}")
                    print(f"Stop loss: {stop_loss:.5f}")
                    print(f"Take profit: {take_profit:.5f}")
                    print("-" * 30)
                
                if sell_condition.iloc[-1]:
                    print("Sell condition met:")
                    current_price = df['close'].iloc[-1]
                    stop_loss = current_price + 1500 * symbol_info.point
                    take_profit = current_price - 1000* symbol_info.point
                    await self.send(text_data=json.dumps({
                                                'status': True,
                                                'condition':'SELL',
                                                'RSI':rsi.rsi.iloc[-1],
                                                'Current Price': current_price,
                                                'SL': stop_loss,
                                                'TP': take_profit
                                                }))

                    print(f"RSI: {rsi.rsi.iloc[-1]:.2f} (below 22)")
                    print(f"Current price: {current_price:.5f}")
                    print(f"Stop loss: {stop_loss:.5f}")
                    print(f"Take profit: {take_profit:.5f}")
                    print("-" * 30)
                await asyncio.sleep(2)  # wait for 60 seconds
       
        except Exception:
            await self.send(text_data=json.dumps({
                'message': 'fail'
            }))
            await self.close()
 

