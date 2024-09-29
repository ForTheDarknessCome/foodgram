from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.filters import OrderingFilter

from cooking.models import (
    Ingredient, Recipe, RecipeIngredient,
    ShoppingCart, Tag
)
from cooking.serializers import (
    FavoriteSerializer, IngredientSerializer,
    RecipeSerializer, ShoppingCartSerializer,
    TagSerializer
)
from utils.filters import RecipeFilter
from utils.link_shortener import LinkShortener
from utils.pagination import CustomLimitOffsetPagination
from utils.permissions import IsAuthorOrReadOnly


link_shortener = LinkShortener()


class RecipeGetShortLinkView(APIView):
    """ Апи-класс для получения короткой ссылки. """
    permission_classes = (AllowAny,)

    def get(self, request, id):
        full_link = f"/api/recipes/{id}/"
        short_link = link_shortener.shorten_url(full_link)
        return Response({"short-link": short_link}, status=status.HTTP_200_OK)


class RecipeGetFullLinkView(APIView):
    """ Апи-класс для обработки коротких ссылок. """
    permission_classes = (AllowAny,)

    def get(self, request, short_code):
        full_url = link_shortener.restore_url(f"s/{short_code}")
        if full_url:
            return Response({"full_url": full_url}, status=status.HTTP_200_OK)
        return Response(
            {"error": "URL не найден"}, status=status.HTTP_404_NOT_FOUND
        )


class RecipeViewSet(viewsets.ModelViewSet):
    """ Вьюсет для работы с рецептами, включая скачивание списка покупок. """
    permission_classes = (IsAuthorOrReadOnly,)
    queryset = Recipe.objects.all().prefetch_related(
        'author', 'tags', 'recipe_ingredients__ingredient'
    )
    serializer_class = RecipeSerializer
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    pagination_class = CustomLimitOffsetPagination
    filterset_fields = ('tags__slug', 'author',
                        'is_in_shopping_cart', 'is_favorited')
    filterset_class = RecipeFilter
    ordering = ('-id',)

    def perform_create(self, serializer):
        """Сохраняет рецепт с автоматически заполненым автором. """
        serializer.save(author=self.request.user)

    def post_delete_favorite_cart(self, pk, serializer_class):
        """Обрабатывает добавление и удаление
        рецептов из избранного и корзины. """
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        object = serializer_class.Meta.model.objects.filter(
            user=user, recipe=recipe
        )

        if self.request.method == 'POST':
            serializer = serializer_class(
                data={'user': user.id, 'recipe': pk},
                context={'request': self.request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if self.request.method == 'DELETE':
            if object.exists():
                object.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({'error': 'Этого рецепта нет в списке'},
                            status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['POST', 'DELETE'], detail=True)
    def favorite(self, request, pk):
        """Добавляет или удаляет рецепт из избранного. """
        return self.post_delete_favorite_cart(pk, FavoriteSerializer)

    @action(methods=['POST', 'DELETE'], detail=True)
    def shopping_cart(self, request, pk):
        """Добавляет или удаляет рецепт из корзины. """
        return self.post_delete_favorite_cart(pk, ShoppingCartSerializer)

    @action(methods=['GET'], detail=False,
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        """Скачивает список покупок для пользователя. """
        shopping_carts = ShoppingCart.objects.filter(user=request.user)
        recipe_ids = shopping_carts.values_list('recipe_id', flat=True)
        ingredients = self.generate_shopping_list(recipe_ids)
        return self.create_txt_file(ingredients)

    def generate_shopping_list(self, recipe_ids):
        """Генерирует список ингредиентов для указанных рецептов. """
        ingredients = {}
        recipe_ingredients = RecipeIngredient.objects.filter(
            recipe_id__in=recipe_ids
        )

        for recipe_ingredient in recipe_ingredients:
            ingredient_name = recipe_ingredient.ingredient.name
            amount = recipe_ingredient.amount
            unit = recipe_ingredient.ingredient.measurement_unit

            if ingredient_name in ingredients:
                ingredients[ingredient_name]['amount'] += amount
            else:
                ingredients[ingredient_name] = {
                    'amount': amount,
                    'unit': unit
                }

        return ingredients

    def create_txt_file(self, ingredients):
        """Создает текстовый файл со списком ингредиентов. """
        content = []
        for name, info in ingredients.items():
            line = f"{name} ({info['unit']}) — {info['amount']}"
            content.append(line)

        file_content = "\n".join(content)

        response = HttpResponse(file_content, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.txt"'
        )

        return response


class TagViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                 viewsets.GenericViewSet):
    """ Вьюсет для просмотра тегов. """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)


class IngredientViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):
    """ Вьюсет для просмотра ингредиентов. """
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('name',)
