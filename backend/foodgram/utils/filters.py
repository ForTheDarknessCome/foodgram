from django_filters.rest_framework import FilterSet, CharFilter
from cooking.models import Recipe


class RecipeFilter(FilterSet):
    tags = CharFilter(field_name='tags__slug', lookup_expr='exact')

    class Meta:
        model = Recipe
        fields = ['tags']
