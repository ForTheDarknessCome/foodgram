from djoser.serializers import UserCreateSerializer, UserSerializer
from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers
from django.core.exceptions import ValidationError

from account.models import Avatar
from utils.fields import Base64ImageField

User = get_user_model()


class ExtendedUserCreateSerializer(UserCreateSerializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)

    class Meta(UserCreateSerializer.Meta):
        fields = UserCreateSerializer.Meta.fields + ('first_name', 'last_name', 'email')

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


class ExtendedUserSerializer(UserSerializer):
    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)
    # is_subscribed = 
    avatar = serializers.StringRelatedField(read_only=True)

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('avatar', 'first_name', 'last_name')
