import pandas as pd
import vectorbt as vbt
import datetime
import MetaTrader5 as mt5
import json
from channels.generic.websocket import AsyncWebsocketConsumer
import asyncio
from .models import Conncted_Clients
from channels.db import database_sync_to_async

class PremiumCheckConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.check_connected_clients_and_initiate()

    async def disconnect(self, message):
        await self.disconnect_and_decrement_client()
        await self.close()

    async def receive(self, text_data):
        try:
            client_data = json.loads(text_data)
            if client_data["msg"] == "ping" and self.task_running == False:
                self.task_running = True
                self.send_task = asyncio.create_task(self.get_buy_or_sell_signal())

            elif client_data["msg"] != "ping":
                await self.send(text_data=json.dumps({'message': f"error"}))
                await self.close()

            elif client_data["msg"] != "ping" and self.task_running:
                await self.send(text_data=json.dumps({'status': False}))
        except Exception:
            await self.close()

    async def get_buy_or_sell_signal(self):
        symbol = "XAUUSD"
        while True:
            await self.send(text_data=json.dumps({
                                                    'status': False,
                                                    'message': "no signal yet"
                                                }))
            print("Getting data in progress...")
            # Get the latest data
            bars = mt5.copy_rates_from(symbol, mt5.TIMEFRAME_M1, datetime.datetime.now(), 365)
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
            await asyncio.sleep(60)  # wait for 60 seconds


    async def check_connected_clients_and_initiate(self):
        clients = await database_sync_to_async(Conncted_Clients.objects.all)()
        count = await database_sync_to_async(clients.count)()      
        self.send_task = False
        self.task_running = False 

        if count == 0:
            obj = await database_sync_to_async(Conncted_Clients.objects.create)(count=1)
        else:
            obj = await database_sync_to_async(Conncted_Clients.objects.first)()
            obj.count += 1
            await database_sync_to_async(obj.save)()
        # if obj.count == 1:
        #     if not mt5.initialize("C:\\Program Files\\MetaTrader 5\\terminal64.exe"):
        #         print('why')
        #         await self.send(text_data=json.dumps({'message': f"error"}))
        #         # quit()
        #         await self.close()

    async def disconnect_and_decrement_client(self):
        obj = await database_sync_to_async(Conncted_Clients.objects.first)()
        print(f'socket closed {obj.count}')

        if obj.count > 1 and self.send_task:
            self.send_task.cancel()

        elif obj.count == 1 and self.send_task:
            self.send_task.cancel()
            # mt5.shutdown()

        obj.count -= 1
        await database_sync_to_async(obj.save)()

class FreeCheckConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # try:
        await self.accept()
        await self.check_connected_clients_and_initiate()
        # except Exception as e:
        #     print(e)

    async def disconnect(self, message):
        await self.disconnect_and_decrement_client()
        await self.close()

    async def receive(self, text_data):
        try:
            client_data = json.loads(text_data)
            if client_data["msg"] == "ping" and self.task_running == False:
                self.task_running = True
                self.send_task = asyncio.create_task(self.get_buy_or_sell_signal())

            elif client_data["msg"] != "ping":
                await self.send(text_data=json.dumps({'message': f"error"}))
                await self.close()

            elif client_data["msg"] != "ping" and self.task_running:
                await self.send(text_data=json.dumps({'status': False}))
        except Exception:
            await self.close()

    async def get_buy_or_sell_signal(self):
        try:
            while True:
                await self.send(text_data=json.dumps({
                                                        'status': False,
                                                        'message': "no signal yet"
                                                    }))
                symbol = 'XAUUSD'  # or any other valid symbol
                symbol_info = mt5.symbol_info(symbol)
                print("Getting data in progress...")
                # Get the latest data
                bars = mt5.copy_rates_from(symbol, mt5.TIMEFRAME_M1, datetime.datetime.now(), 365)
                df = pd.DataFrame(bars)
                df['time'] = pd.to_datetime(df['time'], unit='s')
                df = df.set_index('time')

                # Calculate RSI
                rsi = vbt.RSI.run(df['close'], 14)
                
                # Check buy condition
                buy_condition = rsi.rsi > 78
                
                # Check sell condition
                sell_condition = rsi.rsi < 22

                
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
                await asyncio.sleep(60)  # wait for 60 seconds
        except Exception:
            await self.close()
 
    async def check_connected_clients_and_initiate(self):
        clients = await database_sync_to_async(Conncted_Clients.objects.all)()
        count = await database_sync_to_async(clients.count)()      
        self.send_task = False
        self.task_running = False 

        if count == 0:
            obj = await database_sync_to_async(Conncted_Clients.objects.create)(count=1)
        else:
            obj = await database_sync_to_async(Conncted_Clients.objects.first)()
            obj.count += 1
            await database_sync_to_async(obj.save)()
        # if obj.count == 1:
        #     if not mt5.initialize("C:\\Program Files\\MetaTrader 5\\terminal64.exe"):
        #         await self.send(text_data=json.dumps({'message': f"error"}))
        #         # quit()
        #         await self.close()

    async def disconnect_and_decrement_client(self):
        obj = await database_sync_to_async(Conncted_Clients.objects.first)()
        print(f'socket closed {obj.count}')

        if obj.count > 1 and self.send_task:
            self.send_task.cancel()

        elif obj.count == 1 and self.send_task:
            self.send_task.cancel()
            # mt5.shutdown()

        obj.count -= 1
        await database_sync_to_async(obj.save)()
