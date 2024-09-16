from rest_framework import serializers
from cooking.models import Recipe, Tag, Ingredient
from utils.fields import Base64ImageField


class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=True, allow_null=True,)

    class Meta:
        model = Recipe
        fields = ('name', 'text', 'image', 'cooking_time', 'tags', 'ingredients', 'author')


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')
