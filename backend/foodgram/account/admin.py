from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from account.models import Follow, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Админка для управления моделью User.
    Используется для отображения и редактирования данных пользователей.
    """

    model = User
    list_display = ('username', 'email', 'is_staff', 'is_active')
    list_editable = ('is_active',)
    list_filter = ('is_staff', 'is_active')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)
    fieldsets = (
        (
            'Личная информация',
            {
                'fields': (
                    'email',
                    'first_name',
                    'last_name',
                    'is_active',
                    'is_staff',
                ),
                'description': 'Личные данные пользователя',
            },
        ),
        (
            'Важные даты',
            {
                'fields': ('date_joined',),
                'description': 'Дата регистрации',
            },
        ),
        (
            'Изменение пароля',
            {
                'fields': ('password',),
                'description': 'Измените пароль для пользователя.',
            },
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': ('username', 'email', 'password1', 'password2'),
            },
        ),
    )


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """Админка для управления моделью Follow.
    Используется для отображения и изменения подписок.
    """

    model = Follow
    list_display = ('user', 'following')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')
