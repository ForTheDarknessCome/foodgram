from django.urls import path, include
from rest_framework.routers import DefaultRouter

from cooking.views import (
    IngredientViewSet, RecipeGetShortLinkView,
    RecipeViewSet, TagViewSet
)


router_v1 = DefaultRouter()

router_v1.register(r'recipes', RecipeViewSet, basename='recipes')
router_v1.register(r'tags', TagViewSet, basename='tags')
router_v1.register(r'ingredients', IngredientViewSet, basename='ingredients')


urlpatterns = [
    path('recipes/<int:id>/get-link/', RecipeGetShortLinkView.as_view()),
    path('', include(router_v1.urls)),
]
