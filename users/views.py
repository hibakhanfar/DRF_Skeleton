from rest_framework import status, permissions
from rest_framework.response import Response
from .serializers import RegisterSerializer,UserProfileSerializer
from rest_framework.views import APIView
from .Component import register_user


class RegisterView(APIView):
  permission_classes = [permissions.AllowAny]

  def post(self, request):
      serializer = RegisterSerializer(data=request.data)
      if serializer.is_valid():

          user = register_user(
              username=serializer.validated_data['username'],
              email=serializer.validated_data['email'],
              password=serializer.validated_data['password']
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


class UserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)