from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from django.views.decorators.gzip import gzip_page
from .models import Trade_History
from .serializers import Trade_HistorySerializer

@method_decorator(gzip_page, name='dispatch')
class Seller_OrderHistoryAPI(APIView):
    def get(self, request):
        try:
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


