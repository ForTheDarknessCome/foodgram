from django.db.models import BooleanField, ExpressionWrapper, Q
from django_filters.rest_framework import (
    BooleanFilter,
    CharFilter,
    FilterSet,
    NumberFilter,
)
from django_filters.rest_framework.filters import AllValuesMultipleFilter

from cooking.models import Ingredient, Recipe


class IngredientFilter(FilterSet):
    """Фильтр ингредиентов по названию."""

    name = CharFilter(method='filter_name')

    class Meta:
        model = Ingredient
        fields = ('name',)

    def filter_name(self, queryset, name, value):
        """Метод возвращает кверисет с заданным именем ингредиента."""
        return queryset.filter(
            Q(name__istartswith=value) | Q(name__icontains=value)
        ).annotate(
            startswith=ExpressionWrapper(
                Q(name__istartswith=value),
                output_field=BooleanField()
            )
        ).order_by('-startswith')


class RecipeFilter(FilterSet):
    """Кастомный фильтрсет для фильтрации рецептов."""

    tags = AllValuesMultipleFilter(field_name='tags__slug')
    author = NumberFilter(
        field_name='author__id',
    )
    is_in_shopping_cart = BooleanFilter(method='filter_shopping_cart')
    is_favorited = BooleanFilter(method='filter_favorites')

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_in_shopping_cart', 'is_favorited')

    def filter_shopping_cart(self, queryset, name, value):
        """Фильтрация по наличию в корзине."""
        if value:
            return queryset.filter(is_in_shopping_cart=True)
        return queryset.exclude(is_in_shopping_cart=True)

    def filter_favorites(self, queryset, name, value):
        """Фильтрация по избранным рецептам."""
        if value:
            return queryset.filter(is_favorited=True)
        return queryset.exclude(is_favorited=True)
