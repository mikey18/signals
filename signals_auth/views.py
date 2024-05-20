from django.shortcuts import render

from django.shortcuts import render
from .models import CustomUser
from .serializers import UserSerializer, UserNullSerializer
from .utils import hash_password

from rest_framework.generics import GenericAPIView, CreateAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework.authtoken.models import Token
from rest_framework import generics,status,views,permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .serializers import RegisterSerializer,LoginSerializer,LogoutSerializer
from drf_spectacular.utils import extend_schema



# class CreateUser(GenericAPIView):
#     queryset = CustomUser.objects.all()
#     serializer_class = UserSerializer

#     def post(self, request, *args, **kwargs):
#         serializer = self.serializer_class(data=request.data, context={"request", request})
#         if serializer.is_valid(raise_exception=True):
#             user = CustomUser.objects.create_superuser(**serializer.validated_data)
#             user.save()
#         return Response({
#             # "user_id": username.id,
#             "data": f"User with {user.email} successfully created"
#         })

# class AddAdminUser(GenericAPIView):
#     """
#     Gives user admin permission
#     """
#     permission_classes = [IsAdminUser]
#     queryset = CustomUser.objects.all()
#     serializer_class = UserNullSerializer

#     def patch(self, request, pk, format=None): # Give specific user admin privilege
#         instance = self.get_object()
#         if instance is None:
#             return Response({"detail": "User with 'ID' does not exist"})
#         else:
#             instance.is_staff = True
#             instance.save()
#         return Response({
#             "User": instance.email,
#             "is_admin": instance.is_staff
#         })

# class RemoveAdminUser(GenericAPIView):
#     """
#     Remove user admin permission
#     """
#     permission_classes = [IsAdminUser]
#     queryset = CustomUser.objects.all()
#     serializer_class = UserNullSerializer

#     def delete(self, request, pk, format=None): # Remove admin privilege from selected user
#         instance = self.get_object()
#         if instance is None:
#             return Response({"detail": "User with 'ID' does not exist"})
#         else:
#             instance.is_staff = False
#             instance.save()
#         return Response({
#             "User": instance.email,
#             "is_admin": instance.is_staff
#         })

# Get all admin user
class Users(GenericAPIView):
    """
    Returns all admin users in the database
    """
    queryset = CustomUser.objects.all()
    serializer_class = UserNullSerializer

    def get(self, request, *args, **kwargs):
        global series # set the global series
        admin_list = list()
        series = 1

        for admin in self.queryset.all():
            sery = str(series)
            admin_list.append({
                "user" + sery + "--user_id": admin.id,
                "user" + sery + "--user_email": admin.email,
            })
            int(series)
            series += 1
        return Response({"detail": admin_list})
    
class RegisterView(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    @extend_schema(request=serializer_class, responses=serializer_class)
    def post(self,request):
        user=request.data
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user_data = serializer.data
        return Response(user_data, status=status.HTTP_201_CREATED)

class LoginAPIView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    @extend_schema(request=serializer_class, responses=serializer_class)
    def post(self,request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data,status=status.HTTP_200_OK)

class LogoutAPIView(generics.GenericAPIView):
    serializer_class = LogoutSerializer
    permission_classes = (permissions.IsAuthenticated,)

    @extend_schema(request=serializer_class, responses=serializer_class)
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
