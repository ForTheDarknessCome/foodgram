from django.contrib.auth import get_user_model
from django.db.models import Count
from django.shortcuts import get_object_or_404

from djoser.serializers import SetPasswordSerializer
from rest_framework import mixins, generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from account.models import Follow
from api.serializers.account import (
    AvatarSerializer,
    ExtendedUserCreateSerializer,
    FollowSerializer,
    FollowersSerializer,
    UserSerializer,
)
from utils.pagination import CustomLimitOffsetPagination
from utils.permissions import CurrentUserAdminOrReadOnly


User = get_user_model()


class UserViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """Вьюсет для модели пользователя."""

    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = (CurrentUserAdminOrReadOnly,)
    pagination_class = CustomLimitOffsetPagination

    def get_serializer_class(self):
        if self.action == 'create':
            return ExtendedUserCreateSerializer
        elif self.action == 'set_password':
            return SetPasswordSerializer
        return self.serializer_class

    @action(['post'], detail=False, permission_classes=[IsAuthenticated])
    def set_password(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.request.user.set_password(serializer.data['new_password'])
        self.request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False, methods=['get'], permission_classes=[IsAuthenticated]
    )
    def me(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(user, context={'request': request})
        return Response(serializer.data)

    @action(
        detail=False,
        methods=['put', 'delete'],
        permission_classes=[IsAuthenticated],
        url_path='me/avatar',
    )
    def avatar(self, request, *args, **kwargs):
        """Добавление обновление и удаление аватара пользователя."""
        user = request.user

        if request.method == 'PUT':
            serializer = AvatarSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            user.avatar = serializer.validated_data['avatar']
            user.save()

            return Response(
                {'avatar': user.get_photo_url()}, status=status.HTTP_200_OK
            )
        if user.avatar:
            user.avatar.delete()

        user.save()

        return Response(
            {'status': 'Аватар удален'}, status=status.HTTP_204_NO_CONTENT
        )

    def create(self, request, *args, **kwargs):
        """Функция для создание нового пользователя."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class FollowersList(generics.ListAPIView):
    """Дженерик для отображения списка подписок."""

    serializer_class = FollowersSerializer
    pagination_class = CustomLimitOffsetPagination

    def get_queryset(self):
        user = self.request.user
        queryset = (
            Follow.objects.filter(user=user)
            .prefetch_related('following__recipes')
            .annotate(recipes_count=Count('following__recipes', distinct=True))
        )

        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        recipes_limit = self.request.query_params.get('recipes_limit', None)
        context['recipes_limit'] = recipes_limit
        return context


class FollowView(generics.CreateAPIView, generics.DestroyAPIView):
    """Дженерик для создания и удаления подписки."""

    queryset = Follow.objects.all()
    serializer_class = FollowSerializer

    def get_following_user(self):
        following_id = self.kwargs.get('following_id')
        try:
            following_user = User.objects.annotate(
                recipes_count=Count('recipes')
            ).get(pk=following_id)
        except User.DoesNotExist:
            return get_object_or_404(User, pk=following_id)
        return following_user

    def get_serializer_context(self):
        context = super().get_serializer_context()
        recipes_limit = self.request.query_params.get('recipes_limit', None)
        context['recipes_limit'] = recipes_limit
        return context

    def post(self, request, *args, **kwargs):
        user = request.user
        following_user = self.get_following_user()

        if user == following_user:
            raise ValidationError('Невозможно подписаться на себя')

        if Follow.objects.filter(user=user, following=following_user).exists():
            raise ValidationError('Вы уже подписаны на этого пользователя')

        serializer = FollowSerializer(
            data={'user': user.id, 'following': following_user.id},
            context=self.get_serializer_context(),
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        recipes_count = following_user.recipes_count

        response_data = {**serializer.data, 'recipes_count': recipes_count}

        return Response(response_data, status=status.HTTP_201_CREATED)

    def delete(self, request, following_id, *args, **kwargs):

        deleted_count, _ = Follow.objects.filter(
            user=request.user, following=following_id
        ).delete()

        if deleted_count > 0:
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(
            {'error': 'Вы не подписаны на этого пользователя'},
            status=status.HTTP_400_BAD_REQUEST,
        )
