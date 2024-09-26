from django.urls import path, include
from rest_framework.routers import DefaultRouter

from cooking.views import RecipeViewSet, TagViewSet, IngredientViewSet, RecipeGetShortLinkView #FavoriteAPIView, ShoppingCartAPIView, DownloadShoppingCartView

router_v1 = DefaultRouter()

router_v1.register(r'recipes', RecipeViewSet, basename='recipes')
router_v1.register(r'tags', TagViewSet, basename='tags')
router_v1.register(r'ingredients', IngredientViewSet, basename='ingredients')


urlpatterns = [
    path('recipes/<int:id>/get-link/', RecipeGetShortLinkView.as_view()),
    # path('recipes/<int:id>/favorite/', FavoriteAPIView.as_view()),
    # path('recipes/<int:id>/shopping_cart/', ShoppingCartAPIView.as_view()),
    # path('recipes/download_shopping_cart/', DownloadShoppingCartView.as_view()),
    path('', include(router_v1.urls)),
]

# cooking_patterns = [
#     path('recipes', include(recipes_urls))
# ]
