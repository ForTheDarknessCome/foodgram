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
    photo = models.ImageField(
        upload_to='users/',
        null=True,
        default=None
    )
    user = models.OneToOneField(
        User, related_name='avatar',
        on_delete=models.CASCADE
    )

    def get_photo_url(self):
        return self.photo.url if self.photo else None


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        related_name='following', on_delete=models.CASCADE
    )

    following = models.ForeignKey(
        User,
        related_name='followers', on_delete=models.CASCADE
    )
