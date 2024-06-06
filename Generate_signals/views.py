from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from django.views.decorators.gzip import gzip_page
from .models import Trade_History
from .serializers import Trade_HistorySerializer
from fcm_django.models import FCMDevice
from firebase_admin.messaging import Message

@method_decorator(gzip_page, name='dispatch')
class Seller_OrderHistoryAPI(APIView):
    def get(self, request):
        try:
            # devices = FCMDevice.objects.first()
            # if devices:
            #     message_data = {
            #         "badge": "https://res.cloudinary.com/dmxpt5tfh/image/upload/v1702167641/Miqet%20Notification%20Icon/s20du3xtzpirnb3iw68g.png",
            #         "title": self.kwargs.get("title", ""),
            #         "body": self.kwargs.get("body", ""),
            #         "image": self.kwargs.get("image", ""),
            #         "icon": self.kwargs.get("icon", ""),
            #         "url": self.kwargs.get("url", ""),
            #         "action": self.kwargs.get("action", ""),
            #         "recipient": self.kwargs.get("recipient", "")
            #     }
            #     message = Message(data=message_data)
            #     # for device in devices:
            #     devices.send_message(message)

            orders = Trade_History.objects.all().order_by('-created_at')[:7]
            serializer = Trade_HistorySerializer(orders, many=True)
            return Response({
                'status': 200,
                'data': serializer.data
            })
        except Exception as e:
            print(e)
            return Response({
                'status': 400
            })


