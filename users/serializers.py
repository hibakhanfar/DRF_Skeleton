from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User
from rest_framework.exceptions import ValidationError
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
import magic

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
        fields = ('id', 'username', 'email','is_verified')
        read_only_fields = ('id', 'username', 'email','is_verified')



class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        if not self.user.is_verified:
            raise AuthenticationFailed("Please verify your email address before logging in.")

        return data



class FileSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ( 'username','file')
        read_only_fields = ('username',)

    def validate_file(self, value):
        if value:
            allowed_mime_types = [
                'image/png',
                'image/jpeg',
                'application/pdf',
            ]

            file_mime_type = magic.from_buffer(value.read(2048), mime=True)
            value.seek(0)

            if file_mime_type not in allowed_mime_types:
                raise ValidationError(
                    f'Unsupported file type: {file_mime_type}. Allowed: PNG, JPEG,'
                    ' PDF.'
                )

            return value
