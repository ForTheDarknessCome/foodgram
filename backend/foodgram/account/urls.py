from django.urls import re_path, path, include
from rest_framework_simplejwt import views
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views

from account.views import SignoutView, SigninView, UserViewSet, UserAvatarView, FollowersList, FollowView

router = DefaultRouter()


router.register('', UserViewSet, basename='user')

account_patterns = [
    path('me/avatar/', UserAvatarView.as_view(), name='user-avatar'),
    path('subscriptions/', FollowersList.as_view(), name='followers-list'),
    path('<int:following_id>/subscribe/', FollowView.as_view(), name='follow'),
    path('', include(router.urls)),
]

auth_patterns = [
    path('token/login/', SigninView.as_view(), name="signin"),
    # re_path(r"^token/refresh/?", views.TokenRefreshView.as_view(), name="jwt-refresh"),
    # re_path(r"^token/verify/?", views.TokenVerifyView.as_view(), name="jwt-verify"),
    re_path(r"^token/logout/?", SignoutView.as_view(), name='signout'),
]

urlpatterns = [
    path('users/', include(account_patterns)),
    path('auth/', include(auth_patterns))
]
