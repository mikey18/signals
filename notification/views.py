from django.utils.decorators import method_decorator
from django.views.decorators.gzip import gzip_page
from rest_framework.views import APIView
from rest_framework.response import Response
from fcm_django.models import FCMDevice
from functions.CustomQuery import get_if_exists

@method_decorator(gzip_page, name='dispatch')
class Register_Push_Notification(APIView):
    def post(self, request):
        try:
            fcm = get_if_exists(FCMDevice,
                registration_id=request.data['vapid_id']
            )
            # this will replace details if the token already exists in the database
            if fcm:
                pass
            else:
                # this will register new token with user
                FCMDevice.objects.create(
                    # name=user.first_name,
                    # user_id=payload['id'],
                    # device_id=request.data['device_id'],
                    registration_id=request.data['vapid_id'],
                    type=request.data['type']
                )
            return Response({
                'status': 200
            })
        except Exception as e:
            print(e)
            return Response({
                'status': 400
            })
