from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async
from firebase_admin.messaging import Message
import asyncio
from django.apps import apps


async def send_notification(*args, **kwargs):
    try:
        FCMDevice = apps.get_model('fcm_django', 'FCMDevice')
        devices = await database_sync_to_async(list)(FCMDevice.objects.filter(active=True))
        if devices:
            message_data = {
                "badge": "",
                "title": kwargs.get("title", ""),
                "body": kwargs.get("body", ""),
                "image": kwargs.get("image", ""),
                "icon": kwargs.get("icon", ""),
            }
            message = await sync_to_async(Message)(data=message_data)
            for device in devices:
                asyncio.create_task(sync_to_async(device.send_message)(message))      
    except Exception as e:
        print(e)