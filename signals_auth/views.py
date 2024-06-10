from .models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer,LoginSerializer
from datetime import datetime, timedelta, timezone
from .functions.auth_functions import auth_encoder, auth_decoder

# from django.views.generic import View
# from django.utils.decorators import method_decorator
# from django.views.decorators.csrf import csrf_exempt
# from django.http import JsonResponse
# import asyncio
# from asgiref.sync import sync_to_async
    
class RegisterView(APIView):
    serializer_class = RegisterSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "status": 200,
            "message": 'Successful',
            "user": serializer.data
        })

class LoginAPIView(APIView):
    serializer_class = LoginSerializer

    def get_token(self, user):
        payload = {
            'id': user.id,
            'exp': datetime.now(timezone.utc) + timedelta(days=30),
            'iat': datetime.now(timezone.utc)
        }
        return auth_encoder(payload)
    
    def bad_response(self):
        return Response({
            "status": 400,
            "message": 'Invalid email or password'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = User.objects.get(email=serializer.validated_data['email'].lower(), is_active=True)
        except Exception:
            return self.bad_response()
        
        if not user.check_password(request.data['password']) or user.is_superuser:
            return self.bad_response()

        return Response({
            "status": 200,
            "token": self.get_token(user)
        })
           
class LogoutAPIView(APIView):
    def post(self, request):
        payload = auth_decoder(request.META.get('HTTP_AUTHORIZATION'))
        user = User.objects.get(id=payload['id'])
        if user is None:
            return Response({
                'status': 400,
                'message': 'Logout Unsuccessful',
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "status": 200,
            'message': 'Logout Successful',
        })
    
    

# @method_decorator(csrf_exempt, name='dispatch')
# class SSE(View):
#     async def fetch_data(self, id, sleep):
#         print(f'Coroutine {id} startin to fetch data.')
#         await asyncio.sleep(sleep)
#         return {
#             'id': id,
#             "data": f"from coroutine {id}"
#         }
    
#     def get_data(self):
#         oo = User.objects.all()
#         seriallizer =UserSerializer(oo, many=True)
#         return seriallizer.data

#     async def post(self, request):
#         # headers = request.headers
#         # body = request.body    
#         results = asyncio.gather(self.fetch_data(1, 1), 
#                                  self.fetch_data(2, 1), 
#                                  self.fetch_data(3, 1))
#         result = await results
#         return JsonResponse({
#             "yoo": await sync_to_async(self.get_data)(),
#             "2": result
#         })