from rest_framework import status, permissions
from rest_framework.response import Response
from .serializers import RegisterSerializer,UserProfileSerializer,EmailVerificationSerializer,CustomTokenObtainPairSerializer
from rest_framework.views import APIView
from .Component import register_user
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
import jwt
from .models import User
from django.conf import settings
from rest_framework_simplejwt.views import TokenObtainPairView

class RegisterView(APIView):
  permission_classes = [permissions.AllowAny]
  serializer_class = RegisterSerializer
  def post(self, request):
      serializer = RegisterSerializer(data=request.data)
      if serializer.is_valid():

          user = register_user(
              username=serializer.validated_data['username'],
              email=serializer.validated_data['email'],
              password=serializer.validated_data['password'],
              request = request
          )

          return Response(
              {
                  "message": "User registered successfully",
                  "data": {
                      "id": user.id,
                      "username": user.username,
                      "email": user.email
                  }
              },
              status=status.HTTP_201_CREATED
          )
      return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmailView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        parameters=[OpenApiParameter(name='token', type=str, location='query', required=True)]
    )
    def get(self, request):
        token = request.GET.get('token')

        if not token:
            return Response(
                {'error': 'Token parameter is missing'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=["HS256"]
            )
            user = User.objects.get(id=payload['user_id'])

            if not user.is_verified:
                user.is_verified = True
                user.save()

            return Response(
                {'message': 'Email successfully activated'},
                status=status.HTTP_200_OK,
            )

        except jwt.ExpiredSignatureError:
            return Response(
                {'error': 'Activation link has expired'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except (jwt.DecodeError, jwt.InvalidTokenError, User.DoesNotExist):
            return Response(
                {'error': 'Invalid token'},
                status=status.HTTP_400_BAD_REQUEST,
            )

class UserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if not request.user.is_verified:
            return Response(
                {"error": "Please verify your email address first."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)




class CustomLoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
