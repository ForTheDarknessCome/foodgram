from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from djoser.views import UserViewSet
from rest_framework.decorators import action

from account.serializers import SigninSerializer, ExtendedUserSerializer, AvatarSerializer
from account.models import Avatar


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


# Нужно ограничить в джосере, во вьюсете юзера пут и патч запросы.
# Настроить через регулярные выражения, либо через экшены доп. эндпоинты от me

class ExtendedUserViewSet(UserViewSet):
    """ Расширенный вьюсет юзера из джосера. """
    http_method_names = ['get', 'post']

    @action(detail=False, methods=['get'])
    def me(self, request, *args, **kwargs):
        user = request.user
        serializer = ExtendedUserSerializer(user)
        return Response(serializer.data)

    # @action(detail=False, methods=['put', 'delete'], url_path='me/avatar', url_name='me_avatar')
    # def me_avatar(self, request, *args, **kwargs):
    #     user = request.user
    #     if request.method == 'PUT':
    #         serializer = AvatarSerializer(data=request.data)
    #         serializer.is_valid(raise_exception=True)
    #         user.avatar = serializer.validated_data['avatar']
    #         user.save()
    #         return Response({'status': 'avatar updated'}, status=status.HTTP_200_OK)
    #     user.avatar = None
    #     user.save()
    #     return Response({'status': 'avatar deleted'}, status=status.HTTP_204_NO_CONTENT)


class UserAvatarView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        serializer = AvatarSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user

        avatar, _ = Avatar.objects.get_or_create(user=user)
        avatar.photo = serializer.validated_data['avatar']
        avatar.save()

        return Response({'status': 'avatar updated'}, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        user = request.user
        Avatar.objects.filter(user=user).delete()

        return Response({'status': 'avatar deleted'}, status=status.HTTP_204_NO_CONTENT)
