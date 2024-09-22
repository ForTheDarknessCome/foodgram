from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import action
from rest_framework import generics
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from djoser.serializers import SetPasswordSerializer

from account.serializers import SigninSerializer, UserSerializer, AvatarSerializer, FollowSerializer, FollowersSerializer, ExtendedUserCreateSerializer
from account.models import Avatar, Follow
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
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = (CurrentUserAdminOrReadOnly,)
    http_method_names = ['get', 'post']

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
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        serializer = AvatarSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user

        avatar, _ = Avatar.objects.get_or_create(user=user)
        avatar.avatar = serializer.validated_data['avatar']
        avatar.save()

        return Response({'status': 'Аватар обновлен'}, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        user = request.user
        Avatar.objects.filter(user=user).delete()

        return Response({'status': 'Аватар удален'}, status=status.HTTP_204_NO_CONTENT)


class FollowersList(generics.ListAPIView):
    queryset = Follow.objects.all()
    serializer_class = FollowersSerializer

    def get_queryset(self):
        user = self.request.user
        return Follow.objects.filter(following=user)


class FollowView(generics.CreateAPIView, generics.DestroyAPIView):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer

    def get_following_user(self):
        following_id = self.kwargs.get('following_id')
        return get_object_or_404(User, pk=following_id)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['following'] = self.get_following_user()
        return context

    def perform_create(self, serializer):
        """Создаёт подписку."""
        following_user = self.get_following_user()
        serializer.save(user=self.request.user, following=following_user)

    def get_object(self):
        """Находит существующую подписку для удаления."""
        following_user = self.get_following_user()
        return get_object_or_404(Follow, user=self.request.user, following=following_user)
