from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

from utils.constants import LENGTH_EMAIL


class User(AbstractUser):
    """Модель пользователя, расширяющая стандартную модель AbstractUser.

    Добавляет поле email с уникальным значением.
    """

    email = models.EmailField(
        _('email address'), unique=True, max_length=LENGTH_EMAIL
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=150,
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=150,
    )
    avatar = models.ImageField(
        'Аватар', upload_to='users/', null=True, default=None
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name', 'avatar')

    def get_photo_url(self):
        """Возвращает URL аватара, если он существует."""
        return self.avatar.url if self.avatar else None

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        constraints = [
            models.UniqueConstraint(
                fields=('username', 'email'), name='unique_user'
            )
        ]

    def __str__(self):
        return self.username


class Follow(models.Model):
    """Модель для хранения подписок пользователей.

    Позволяет отслеживать, кто на кого подписан.
    """

    user = models.ForeignKey(
        User,
        related_name='following',
        on_delete=models.CASCADE,
        verbose_name='Автор',
    )

    following = models.ForeignKey(
        User,
        related_name='followers',
        on_delete=models.CASCADE,
        verbose_name='Подписчик',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'following'], name='unique_follower'
            )
        ]

    def __str__(self):
        return f'Автор: {self.following}, подписчик: {self.user}'
