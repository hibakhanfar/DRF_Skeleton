from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class RegisterSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'email', 'password')
        extra_kwargs = {
            'password': {'write_only': True}
        }
    def validate_password(self, value):
        validate_password(value)
        return value


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email','is_verified','profile_picture')
        read_only_fields = ('id', 'username', 'email','is_verified')


class EmailVerificationSerializer(serializers.ModelSerializer):
    token = serializers.CharField(max_length=555, write_only=True)

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        if not self.user.is_verified:
            raise AuthenticationFailed("Please verify your email address before logging in.")

        return data