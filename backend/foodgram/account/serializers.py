from djoser.serializers import UserCreateSerializer
from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers
from django.core.exceptions import ValidationError
from rest_framework.validators import UniqueTogetherValidator

from cooking.models import Recipe
from account.models import Avatar, Follow
from utils.fields import Base64ImageField

User = get_user_model()


class ExtendedUserCreateSerializer(UserCreateSerializer):
    first_name = serializers.CharField(required=True, max_length=150)
    last_name = serializers.CharField(required=True, max_length=150)
    email = serializers.EmailField(required=True, max_length=254)

    class Meta(UserCreateSerializer.Meta):
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'password')

    def validate_email(self, value):
        """ Проверка уникальности email. """
        if User.objects.filter(email=value).exists():
            raise ValidationError('Этот email уже занят. Пожалуйста, используйте другой.')
        return value

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = super().create(validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user


class SigninSerializer(serializers.Serializer):
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
    avatar = Base64ImageField(required=True)

    class Meta:
        model = Avatar
        fields = ('avatar',)


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'is_subscribed', 'avatar')
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

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowersSerializer(serializers.ModelSerializer):
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
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'is_subscribed', 'recipes', 'recipes_count', 'avatar',)

    def get_avatar(self, obj):
        following_user = obj.following
        if hasattr(following_user, 'avatar') and following_user.avatar:
            return following_user.avatar.get_photo_url()
        return None

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return Follow.objects.filter(user=user, following=obj.following).exists()

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


class FollowSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
        default=serializers.CurrentUserDefault()
    )
    following = serializers.SlugRelatedField(
        queryset=User.objects.all(),
        slug_field='username',
    )

    class Meta:
        model = Follow
        fields = ('user', 'following')
        read_only_fields = ('user',)
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'following'),
                message='Вы уже подписаны на этого пользователя'
            )
        ]

    def validate(self, data):
        user = self.context['request'].user
        following_user = data['following']

        if user == following_user:
            raise serializers.ValidationError('Невозможно подписаться на себя')

        return data

    def to_internal_value(self, data):
        data['following'] = self.context['following'].username
        return super().to_internal_value(data)

    def to_representation(self, instance):
        context = {
            'request': self.context.get('request'),
            'recipes_limit': self.context.get('recipes_limit')
        }
        return FollowersSerializer(instance, context=context).data
