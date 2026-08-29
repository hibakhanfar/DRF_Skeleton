from .models import User


def register_user(username: str, email: str, password: str):
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password
    )
    return user