from django.db import transaction

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from api.serializers.account import UserSerializer
from cooking.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)
from utils.fields import Base64ImageField


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для получения полей тегов."""

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для подробного описания ингредиентов в рецепте."""

    name = serializers.CharField(source='ingredient.name', read_only=True)
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient.id', read_only=True
    )
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit', read_only=True
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class AddIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления существующих ингредиентов в рецепт.
    Используется для определения поля ingredients в RecipeSerializer.
    """

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(), source='ingredient'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для создания рецептов."""

    image = Base64ImageField(required=True, allow_null=True)
    ingredients = AddIngredientSerializer(many=True, required=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
        )
        read_only_fields = ('author',)

    def validate(self, data):
        ingredients = data.get('ingredients', [])
        if not ingredients:
            raise serializers.ValidationError(
                {'ingredients': 'Поле ингредиентов не может быть пустым.'}
            )

        ingredients_list = [item['ingredient'] for item in data['ingredients']]
        if len(ingredients_list) != len(set(ingredients_list)):
            raise serializers.ValidationError(
                {'error': 'Ингредиенты должны быть уникальными'}
            )

        tags = data.get('tags', [])
        if not tags:
            raise serializers.ValidationError(
                {'tags': 'Поле тегов не может быть пустым.'}
            )

        if len(tags) != len(set(tags)):
            raise serializers.ValidationError(
                {'error': 'Теги должны быть уникальными'}
            )
        return data

    def create_ingredients(self, recipe, ingredients):
        RecipeIngredient.objects.bulk_create(
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient.get('ingredient'),
                amount=ingredient.get('amount'),
            )
            for ingredient in ingredients
        )

    @transaction.atomic
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')

        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags_data)

        self.create_ingredients(recipe, ingredients)

        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')

        RecipeIngredient.objects.filter(recipe=instance).delete()

        instance.tags.set(tags)
        self.create_ingredients(instance, ingredients)

        return super().update(instance, validated_data)

    def to_representation(self, instance):
        """Возвращает пользователю полный экземпляр рецепта."""

        return GetRecipeSerializer(instance, context=self.context).data


class RecipeDetailSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения краткой информации о рецепте."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class GetRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения полной информации о рецепте."""

    tags = TagSerializer(many=True)
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        read_only=True, many=True, source='recipe_ingredients'
    )
    is_favorited = serializers.BooleanField(read_only=True)
    is_in_shopping_cart = serializers.BooleanField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )


class BaseRecipeActionSerializer(serializers.ModelSerializer):
    """Базовый сериализатор для действий с рецептами."""

    class Meta:
        fields = ('user', 'recipe')

    def validate(self, data):
        user, recipe = data.get('user'), data.get('recipe')
        if self.Meta.model.objects.filter(user=user, recipe=recipe).exists():
            raise ValidationError({'error': 'Этот рецепт уже добавлен.'})
        return data

    def to_representation(self, instance):
        context = {'request': self.context.get('request')}
        return RecipeDetailSerializer(instance.recipe, context=context).data


class FavoriteSerializer(BaseRecipeActionSerializer):
    """Сериализатор добавления/удаления рецепта в избранное."""

    class Meta(BaseRecipeActionSerializer.Meta):
        model = Favorite


class ShoppingCartSerializer(BaseRecipeActionSerializer):
    """Сериализатор добавления/удаления рецепта в список покупок."""

    class Meta(BaseRecipeActionSerializer.Meta):
        model = ShoppingCart
