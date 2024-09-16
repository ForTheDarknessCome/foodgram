from django.urls import re_path, path, include
from rest_framework_simplejwt import views
from rest_framework.routers import DefaultRouter

from account.views import SignoutView, SigninView, ExtendedUserViewSet, UserAvatarView

router = DefaultRouter()


router.register('', ExtendedUserViewSet, basename='user')

account_patterns = [
    path('', include(router.urls)),
    path('me/avatar/', UserAvatarView.as_view(), name='user-avatar'),
]

auth_patterns = [
    path('token/login/', SigninView.as_view(), name="signin"),
    re_path(r"^token/refresh/?", views.TokenRefreshView.as_view(), name="jwt-refresh"),
    re_path(r"^token/verify/?", views.TokenVerifyView.as_view(), name="jwt-verify"),
    re_path(r"^token/logout/?", SignoutView.as_view(), name='signout'),
]

urlpatterns = [
    path('users/', include(account_patterns)),
    path('auth/', include(auth_patterns))
]
