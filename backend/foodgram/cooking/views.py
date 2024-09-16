from rest_framework import filters, mixins, status, viewsets, views
from cooking.models import Recipe, Tag, Ingredient
from cooking.serializers import RecipeSerializer, TagSerializer, IngredientSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
import rest_framework.generics
from rest_framework import mixins


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    http_method_names = ('get', 'post', 'patch', 'delete')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

# Написать эндпоинты для тегов и ингредиентов через апи вью или через классы.
# Код у них будет дублироваться,
# так что можно вынести его вотдельный класс(миксин)
# просмотреть проблему ед(мн) числа в названии моделей, функций, сериализаторов.


# class TagView(APIView):
#     def get(self, request):
#         tags = Tag.objects.all()
#         serializer = TagSerializer(tags, many=True)
#         return Response(serializer.data)

class TagViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                 viewsets.GenericViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
