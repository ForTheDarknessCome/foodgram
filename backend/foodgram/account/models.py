from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

from utils.constants import AVATAR_VERBOSE_NAME, LENGTH_EMAIL


class User(AbstractUser):
    """Модель пользователя, расширяющая стандартную модель AbstractUser.
    Добавляет поле email с уникальным значением.
    """
    email = models.EmailField(
        _('email address'), unique=True, max_length=LENGTH_EMAIL)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Avatar(models.Model):
    """Модель для хранения аватара пользователя."""
    avatar = models.ImageField(
        AVATAR_VERBOSE_NAME,
        upload_to='users/',
        null=True,
        default=None
    )
    user = models.OneToOneField(
        User, related_name='avatar',
        on_delete=models.CASCADE
    )

    def get_photo_url(self):
        """Возвращает URL аватара, если он существует."""
        return self.avatar.url if self.avatar else None

    class Meta:
        verbose_name = AVATAR_VERBOSE_NAME
        verbose_name_plural = 'Аватарки'

    def __str__(self):
        return f'Пользователь {self.user}: аватар {self.get_photo_url()}'


class Follow(models.Model):
    """Модель для хранения подписок пользователей.
    Позволяет отслеживать, кто на кого подписан.
    """
    user = models.ForeignKey(
        User,
        related_name='following', on_delete=models.CASCADE,
        verbose_name='Автор'
    )

    following = models.ForeignKey(
        User,
        related_name='followers', on_delete=models.CASCADE,
        verbose_name='Подписчик'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'following'],
                name='unique_follower')
        ]

    def __str__(self):
        return f'Автор: {self.following}, подписчик: {self.user}'
