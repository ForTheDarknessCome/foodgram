from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class EmailBackend(ModelBackend):
    """Класс для аутентификации пользователей по email вместо
    стандартного логина."""
    def authenticate(self, request, email=None, password=None):
        """Метод аутентификации. Возвращает пользователя, если
        email и пароль верны, иначе возвращает None."""

        User = get_user_model()
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return None

        if user.check_password(password):
            return user
        else:
            return None
