from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from django.views.decorators.gzip import gzip_page
from rest_framework.pagination import LimitOffsetPagination
from .models import Trade_History
from .serializers import Trade_HistorySerializer

@method_decorator(gzip_page, name='dispatch')
class Seller_OrderHistoryAPI(APIView, LimitOffsetPagination):
    def get(self, request):
        try:
            orders = Trade_History.objects.all().order_by('-created_at')
            results = self.paginate_queryset(orders, request, view=self)
            serializer = Trade_HistorySerializer(results, many=True)
            return self.get_paginated_response(serializer.data)
        except Exception:
            return Response({
                'status': 400
            })


