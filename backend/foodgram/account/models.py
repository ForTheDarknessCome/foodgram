# from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.db import models


# User = get_user_model()


class User(AbstractUser):
    email = models.EmailField(_('email address'), unique=True)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Avatar(models.Model):
    avatar = models.ImageField(
        'Аватар',
        upload_to='users/',
        null=True,
        default=None
    )
    user = models.OneToOneField(
        User, related_name='avatar',
        on_delete=models.CASCADE
    )

    def get_photo_url(self):
        return self.avatar.url if self.avatar else None

    class Meta:
        verbose_name = 'Аватар'
        verbose_name_plural = 'Аватарки'

    def __str__(self):
        return f'Пользователь {self.user}: аватар {self.get_photo_url()}'


class Follow(models.Model):
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
