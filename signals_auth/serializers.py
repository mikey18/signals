from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'fullname']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=68, min_length=6, write_only=True)
    class Meta:
        model = User
        fields = ['email', 'fullname', 'password']

    def create(self, validated_data):
        email = validated_data.get('email')
        if email:
            validated_data['email'] = email.lower()
        password = validated_data.pop('password', None)
        # as long as the fields are the same, we can just use this
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=255, min_length=3)
    password = serializers.CharField(max_length=68, min_length=6)

class UserNullSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = []


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    # def validate(self, attrs):
    #     self.token = attrs['refresh']
    #     return attrs
    # def save(self, **kwargs):
    #     try:
    #         RefreshToken(self.token).blacklist()
    #     except TokenError:
    #         self.fail('bad_token')