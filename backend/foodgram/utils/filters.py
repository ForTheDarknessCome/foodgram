from django_filters.rest_framework import (
    BooleanFilter, CharFilter, FilterSet, NumberFilter
)

from cooking.models import Recipe


class RecipeFilter(FilterSet):
    """ Кастомный фильтрсет для фильтрации рецептов. """
    tags = CharFilter(field_name='tags__slug', lookup_expr='exact')
    author = NumberFilter(field_name='author__id',)
    is_in_shopping_cart = BooleanFilter(method='filter_shopping_cart')
    is_favorited = BooleanFilter(method='filter_favorites')

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_in_shopping_cart', 'is_favorited')

    def filter_shopping_cart(self, queryset, name, value):
        """Фильтрация по наличию в корзине. """
        user = self.request.user
        if user.is_authenticated:
            if value:
                return queryset.filter(shopping_cart__user=user).distinct()
            else:
                return queryset.exclude(shopping_cart__user=user).distinct()
        return queryset

    def filter_favorites(self, queryset, name, value):
        """Фильтрация по избранным рецептам. """
        user = self.request.user
        if user.is_authenticated:
            if value:
                return queryset.filter(favorite__user=user).distinct()
            else:
                return queryset.exclude(favorite__user=user).distinct()
        return queryset
