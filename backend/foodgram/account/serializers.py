from django.contrib.auth import authenticate, get_user_model
from django.core.exceptions import ValidationError

from djoser.serializers import UserCreateSerializer
from rest_framework import serializers

from account.models import Avatar, Follow
from cooking.models import Recipe
from utils.constants import LENGTH_EMAIL, LENGTH_NAME
from utils.fields import Base64ImageField

User = get_user_model()


class ExtendedUserCreateSerializer(UserCreateSerializer):
    """ Расширенный сериализатор для создания пользователя. """
    first_name = serializers.CharField(required=True, max_length=LENGTH_NAME)
    last_name = serializers.CharField(required=True, max_length=LENGTH_NAME)
    email = serializers.EmailField(required=True, max_length=LENGTH_EMAIL)

    class Meta(UserCreateSerializer.Meta):
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'password')

    def validate_email(self, value):
        """ Проверка уникальности email. """
        if User.objects.filter(email=value).exists():
            raise ValidationError(
                'Email занят. Пожалуйста, используйте другой.'
            )
        return value

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = super().create(validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user


class SigninSerializer(serializers.Serializer):
    """ Сериализатор для аутентификации по имэйлу и паролю. """
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(email=email, password=password)

        if not user:
            raise serializers.ValidationError('Неверные данные для входа.')

        attrs['user'] = user
        return attrs


class AvatarSerializer(serializers.ModelSerializer):
    """ Сериализатор для поля аватар. """
    avatar = Base64ImageField(required=True)

    class Meta:
        model = Avatar
        fields = ('avatar',)


class UserSerializer(serializers.ModelSerializer):
    """ Сериализатор для работы с пользователями. """
    is_subscribed = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'avatar')
        read_only_fields = ('id', 'first_name', 'last_name')

    def get_avatar(self, obj):
        if hasattr(obj, 'avatar') and obj.avatar is not None:
            return obj.avatar.get_photo_url()
        return None

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return Follow.objects.filter(user=user, following=obj).exists()
        return False


class RecipeDetailSerializer(serializers.ModelSerializer):
    """ Сериализатор для наследования FollowersSerializer. """

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowersSerializer(serializers.ModelSerializer):
    """ Сериализатор для полного отображения информации о фоловерах. """
    email = serializers.EmailField(source='following.email')
    id = serializers.IntegerField(source='following.id')
    username = serializers.CharField(source='following.username')
    first_name = serializers.CharField(source='following.first_name')
    last_name = serializers.CharField(source='following.last_name')
    avatar = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count', 'avatar',)

    def get_avatar(self, obj):
        following_user = obj.following
        if hasattr(following_user, 'avatar') and following_user.avatar:
            return following_user.avatar.get_photo_url()
        return None

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return Follow.objects.filter(
            user=user, following=obj.following
        ).exists()

    def get_recipes(self, obj):
        following_user = obj.following
        recipes_limit = self.context.get('recipes_limit')

        recipes = Recipe.objects.filter(author=following_user)
        if recipes_limit is not None:
            recipes = recipes[:int(recipes_limit)]

        return RecipeDetailSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        following_user = obj.following
        return Recipe.objects.filter(author=following_user).count()


class FollowSerializer(serializers.Serializer):
    """ Сериализатор для создания подписки.
    Возвращает данные о пользователе, на которого подписались. """

    def to_representation(self, instance):
        """ Вызывает FollowersSerializer для полного отображения профиля. """
        context = {
            'request': self.context.get('request'),
            'recipes_limit': self.context.get('recipes_limit')
        }
        return FollowersSerializer(instance, context=context).data
