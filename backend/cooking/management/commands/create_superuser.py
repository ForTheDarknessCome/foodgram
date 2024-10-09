from django.core.management.base import BaseCommand

from account.models import User


class Command(BaseCommand):
    """Класс для создания суперпользователя при деплое."""

    help = 'Автоматическое создание суперпользователя.'

    def handle(self, *args, **kwargs):
        """Функция обрабочик."""
        username = 'Antharas'
        email = 'Antharas@example.com'
        password = '456852123789Ee'
        is_verified = True

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(
                f'Суперпользователь с никнеймом "{username}" уже существует.'
            ))
        else:
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            user.is_verified = is_verified
            user.save()
            self.stdout.write(self.style.SUCCESS(
                f'Суперпользователь "{username}" успешно создан.'
            ))
