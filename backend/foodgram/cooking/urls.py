from django.urls import path, include
from rest_framework.routers import DefaultRouter

from cooking.views import RecipesViewSet, TagViewSet, IngredientViewSet

router_v1 = DefaultRouter()

router_v1.register('recipes', RecipesViewSet, basename='recipes')
router_v1.register(r'tags', TagViewSet, basename='tags')
router_v1.register(r'ingredients', IngredientViewSet, basename='ingredients')


urlpatterns = [
    path('', include(router_v1.urls)),
    # path('tags', TagView.as_view(), name="tags"),
]