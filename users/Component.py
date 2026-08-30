from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from .services import EmailNotificationService

def register_user(username: str, email: str, password: str,request=None):
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        is_verified = False
    )
    token = RefreshToken.for_user(user).access_token

    relative_link = reverse('email-verify')
    if request:
        domain = get_current_site(request).domain
        absurl = f"http://{domain}{relative_link}?token={str(token)}"
    else:
        absurl = f"http://127.0.0.1:8000{relative_link}?token={str(token)}"

    email_body = f"Hi {user.username},\n\nPlease use the link below to verify your email:\n{absurl}"
    email_data = {
        'email_subject': 'Verify your email',
        'email_body': email_body,
        'to_email': user.email
    }

    EmailNotificationService.send_email(email_data)
    return user