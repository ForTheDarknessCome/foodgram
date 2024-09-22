from rest_framework import filters, mixins, status, viewsets, views
from cooking.models import Recipe, Tag, Ingredient, Favorite, ShoppingCart, RecipeIngredient
from cooking.serializers import RecipeSerializer, TagSerializer, IngredientSerializer, RecipeDetailSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from  rest_framework import generics
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from utils.link_shortener import LinkShortener
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from utils.filters import RecipeFilter
from rest_framework.filters import OrderingFilter


link_shortener = LinkShortener()


class RecipeGetShortLinkView(APIView):

    def get(self, request, id):
        full_link = f"/api/recipes/{id}/"
        short_link = link_shortener.shorten_url(full_link)
        return Response({"short-link": short_link}, status=status.HTTP_200_OK)


class RecipeGetFullLinkView(APIView):
    def get(self, request, short_code):
        full_url = link_shortener.restore_url(f"s/{short_code}")
        if full_url:
            return Response({"full_url": full_url}, status=status.HTTP_200_OK)
        return Response({"error": "URL не найден"}, status=status.HTTP_404_NOT_FOUND)


class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_fields = ('tags__slug', 'author')
    filterset_class = RecipeFilter
    ordering = ('-id',)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class TagViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                 viewsets.GenericViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class BaseRecipeAPIView(APIView):
    """ Апи класс для наследования списка покупок и избранных """
    serializer_class = RecipeDetailSerializer

    def add_to_list(self, request, id, model, response_detail):
        recipe = get_object_or_404(Recipe, pk=id)
        _, created = model.objects.get_or_create(user=request.user, recipe=recipe)

        if created:
            return Response(RecipeDetailSerializer(recipe).data, status=status.HTTP_201_CREATED)
        return Response({"detail": response_detail}, status=status.HTTP_400_BAD_REQUEST)

    def remove_from_list(self, request, id, model, response_detail):
        recipe = get_object_or_404(Recipe, pk=id)

        try:
            item = model.objects.get(user=request.user, recipe=recipe)
            item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except model.DoesNotExist:
            return Response({"detail": response_detail}, status=status.HTTP_404_NOT_FOUND)


class FavoriteAPIView(BaseRecipeAPIView):

    def post(self, request, id):
        return self.add_to_list(
            request, id, Favorite, "Рецепт уже содержится в избранных")

    def delete(self, request, id):
        return self.remove_from_list(
            request, id, Favorite, "Рецепт не в избранных")


class ShoppingCartAPIView(BaseRecipeAPIView):

    def post(self, request, id):
        return self.add_to_list(
            request, id, ShoppingCart,
            "Рецепт уже содержится в списке покупок"
        )

    def delete(self, request, id):
        return self.remove_from_list(
            request, id, ShoppingCart, "Рецепт не в списке покупок"
        )


class DownloadShoppingCartView(APIView):

    def get(self, request, *args, **kwargs):
        shopping_carts = ShoppingCart.objects.filter(user=request.user)
        recipe_ids = shopping_carts.values_list('recipe_id', flat=True)
        return self.generate_shopping_list(recipe_ids)

    def generate_shopping_list(self, recipe_ids):
        ingredients = {}

        recipe_ingredients = RecipeIngredient.objects.filter(recipe_id__in=recipe_ids)

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

        return self.create_txt_file(ingredients)

    def create_txt_file(self, ingredients):
        content = []
        for name, info in ingredients.items():
            line = f"{name} ({info['unit']}) — {info['amount']}"
            content.append(line)

        file_content = "\n".join(content)

        response = HttpResponse(file_content, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="shopping_list.txt"'

        return response
