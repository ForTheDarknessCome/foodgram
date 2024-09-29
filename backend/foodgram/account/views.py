from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from djoser.serializers import SetPasswordSerializer

from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from account.models import Avatar, Follow
from account.serializers import (
    AvatarSerializer, ExtendedUserCreateSerializer, FollowSerializer,
    FollowersSerializer, SigninSerializer, UserSerializer
)
from utils.pagination import CustomLimitOffsetPagination
from utils.permissions import CurrentUserAdminOrReadOnly


User = get_user_model()


class SignoutView(APIView):
    """ Вью-класс для логаута с отправкой 204 на фронтенд. """
    def post(self, request):
        return Response(status=status.HTTP_204_NO_CONTENT)


class SigninView(APIView):
    """ Вью-класс для авторизации с выдачей токена. """
    serializer_class = SigninSerializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        tokens = self.get_token(user)

        return Response(tokens, status=status.HTTP_200_OK)

    def get_token(self, user):
        """ Генерирует токены для пользователя. """
        refresh = RefreshToken.for_user(user)
        return {
            'auth_token': str(refresh.access_token),
        }


class UserViewSet(viewsets.ModelViewSet):
    """ Вьюсет для модели пользователя. """
    serializer_class = UserSerializer
    queryset = User.objects.all().select_related('avatar')
    permission_classes = (CurrentUserAdminOrReadOnly,)
    http_method_names = ['get', 'post']
    pagination_class = CustomLimitOffsetPagination

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        if self.action == 'me' or self.action == 'set_password':
            return [IsAuthenticated()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'create':
            return ExtendedUserCreateSerializer
        elif self.action == 'set_password':
            return SetPasswordSerializer
        return self.serializer_class

    @action(["post"], detail=False)
    def set_password(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.request.user.set_password(serializer.data["new_password"])
        self.request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def me(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(user, context={'request': request})
        return Response(serializer.data)


class UserAvatarView(APIView):
    """ Вью-класс для добавлелия аватарки через PUT запрос. """
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        serializer = AvatarSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user

        avatar, _ = Avatar.objects.get_or_create(user=user)
        avatar.avatar = serializer.validated_data['avatar']
        avatar.save()

        avatar_url = avatar.get_photo_url()

        return Response({"avatar": avatar_url}, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        user = request.user
        Avatar.objects.filter(user=user).delete()

        return Response(
            {'status': 'Аватар удален'},
            status=status.HTTP_204_NO_CONTENT
        )


class FollowersList(generics.ListAPIView):
    """ Дженерик для отображения списка подписок. """
    queryset = Follow.objects.all()
    serializer_class = FollowersSerializer
    pagination_class = CustomLimitOffsetPagination

    def get_queryset(self):
        user = self.request.user
        return Follow.objects.filter(user=user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        recipes_limit = self.request.query_params.get('recipes_limit', None)
        context['recipes_limit'] = recipes_limit
        return context


class FollowView(generics.CreateAPIView, generics.DestroyAPIView):
    """ Дженерик для создания и удаления подписки. """
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer

    def get_following_user(self):
        following_id = self.kwargs.get('following_id')
        return get_object_or_404(User, pk=following_id)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        recipes_limit = self.request.query_params.get('recipes_limit', None)
        context['recipes_limit'] = recipes_limit
        return context

    def post(self, request, *args, **kwargs):
        user = request.user
        following_user = self.get_following_user()

        if user == following_user:
            raise ValidationError("Невозможно подписаться на себя")

        if Follow.objects.filter(user=user, following=following_user).exists():
            raise ValidationError("Вы уже подписаны на этого пользователя")

        follow_instance = Follow.objects.create(
            user=user, following=following_user
        )
        serializer = FollowSerializer(
            follow_instance,
            context=self.get_serializer_context()
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        following_user = self.get_following_user()

        follow_instance = Follow.objects.filter(
            user=request.user, following=following_user
        ).first()

        if follow_instance:
            follow_instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(
            {'error': 'Вы не подписаны на этого пользователя'},
            status=status.HTTP_400_BAD_REQUEST
        )
