from django.urls import path, include

from rest_framework.routers import DefaultRouter
from djoser.views import TokenCreateView, TokenDestroyView

from api.views.account import FollowersList, FollowView, UserViewSet

from api.views.cooking import (
    IngredientViewSet,
    RecipeGetShortLinkView,
    RecipeViewSet,
    TagViewSet,
)


router_v1 = DefaultRouter()

router_v1.register(r'users', UserViewSet, basename='user')
router_v1.register(r'recipes', RecipeViewSet, basename='recipes')
router_v1.register(r'tags', TagViewSet, basename='tags')
router_v1.register(r'ingredients', IngredientViewSet, basename='ingredients')

account_patterns = [
    path('subscriptions/', FollowersList.as_view(), name='followers-list'),
    path('<int:following_id>/subscribe/', FollowView.as_view(), name='follow'),
]

auth_patterns = [
    path('token/login/', TokenCreateView.as_view(), name='signin'),
    path('^token/logout/?', TokenDestroyView.as_view(), name='signout'),
]

urlpatterns = [
    path('users/', include(account_patterns)),
    path('auth/', include('djoser.urls.authtoken')),
    path('recipes/<int:id>/get-link/', RecipeGetShortLinkView.as_view()),
    path('', include(router_v1.urls)),
]
