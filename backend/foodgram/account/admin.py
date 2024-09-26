from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from account.models import User, Follow, Avatar


class UserAdmin(BaseUserAdmin):
    model = User
    list_display = ('username', 'email', 'is_staff', 'is_active')
    list_editable = ('is_active',)
    list_filter = ('is_staff', 'is_active')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)
    fieldsets = (
        ('Личная информация', {
            'fields': ('email', 'first_name', 'last_name', 'is_active', 'is_staff'),
            'description': 'Личные данные пользователя',
        }),
        ('Важные даты', {
            'fields': ('date_joined',),
            'description': 'Дата регистрации',
        }),
        ('Изменение пароля', {
            'fields': ('password',),
            'description': 'Измените пароль для пользователя.',
        }),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )


class AvatarAdmin(admin.ModelAdmin):
    model = Avatar
    list_display = ('user', 'avatar')
    list_filter = ('user__is_staff', 'user__is_active')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')


class FollowAdmin(admin.ModelAdmin):
    model = Follow
    list_display = ('user', 'following')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')


admin.site.register(User, UserAdmin)
admin.site.register(Follow, FollowAdmin)
admin.site.register(Avatar, AvatarAdmin)
