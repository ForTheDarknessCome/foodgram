from django.urls import path, include

from rest_framework.routers import DefaultRouter
from djoser.views import TokenCreateView, TokenDestroyView

from account.views import (
    FollowersList, FollowView, UserViewSet
)


router = DefaultRouter()


router.register('', UserViewSet, basename='user')

account_patterns = [
    path('subscriptions/', FollowersList.as_view(), name='followers-list'),
    path('<int:following_id>/subscribe/', FollowView.as_view(), name='follow'),
    path('', include(router.urls)),
]

auth_patterns = [
    path('token/login/', TokenCreateView.as_view(), name='signin'),
    path('^token/logout/?', TokenDestroyView.as_view(), name='signout'),
]

urlpatterns = [
    path('users/', include(account_patterns)),
    path('auth/', include('djoser.urls.authtoken')),
]
