from django.urls import path

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import *
urlpatterns = [

    path('register/', RegisterView.as_view(), name='register'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', UserProfileView.as_view(), name='user_profile'),
    path('email-verify/', VerifyEmailView.as_view(), name="email-verify"),
    path('login/', CustomLoginView.as_view(), name='login'),
]