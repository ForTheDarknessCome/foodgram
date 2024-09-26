from rest_framework import serializers
from cooking.models import Recipe, Tag, Ingredient, RecipeIngredient, Favorite, ShoppingCart
from utils.fields import Base64ImageField
from rest_framework.exceptions import ValidationError
from django.db import transaction
from account.serializers import UserSerializer


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для подробного описания ингредиентов в рецепте."""
    name = serializers.CharField(
        source='ingredient.name', read_only=True)
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient.id', read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit', read_only=True)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class AddIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=True, allow_null=True)
    ingredients = AddIngredientSerializer(many=True, required=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'name', 'image', 'text', 'cooking_time')
        read_only_fields = ('author',)

    def validate(self, data):
        ingredients = data.get('ingredients', [])
        if not ingredients:
            raise serializers.ValidationError({'ingredients': 'Поле ингредиентов не может быть пустым.'})

        ingredients_list = [item['ingredient'] for item in data['ingredients']]
        all_ingredients, distinct_ingredients = len(ingredients_list), len(set(ingredients_list))

        if all_ingredients != distinct_ingredients:
            raise ValidationError({'error': 'Ингредиенты должны быть уникальными'})

        tags = data.get('tags', [])
        if not tags:
            raise serializers.ValidationError({'tags': 'Поле тегов не может быть пустым.'})

        all_tags, distinct_tags = len(tags), len(set(tags))
        if all_tags != distinct_tags:
            raise serializers.ValidationError({'error': 'Теги должны быть уникальными'})
        return data

    def get_ingredients(self, recipe, ingredients):
        RecipeIngredient.objects.bulk_create(
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient.get('ingredient'),
                amount=ingredient.get('amount')
            ) for ingredient in ingredients)

    @transaction.atomic
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')

        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags_data)

        self.get_ingredients(recipe, ingredients)

        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')

        RecipeIngredient.objects.filter(recipe=instance).delete()

        instance.tags.set(tags)
        self.get_ingredients(instance, ingredients)

        return super().update(instance, validated_data)

    def to_representation(self, instance):
        """ Возвращает пользователю полный экземпляр рецепта """
        context = {'request': self.context.get('request')}
        return GetRecipeSerializer(instance, context=context).data


class RecipeDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class GetRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения полной информации о рецепте."""
    tags = TagSerializer(many=True)
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(read_only=True, many=True,
                                             source='recipe_ingredients')
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')

    def get_is_favorited(self, object):
        user = self.context.get('request').user
        if user.is_authenticated:
            return object.favorite.filter(user=user).exists()
        return False

    def get_is_in_shopping_cart(self, object):
        user = self.context.get('request').user
        if user.is_authenticated:
            return object.shopping_cart.filter(user=user).exists()
        return False


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор добавления/удаления рецепта в избранное."""
    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

    def validate(self, data):
        user, recipe = data.get('user'), data.get('recipe')
        if self.Meta.model.objects.filter(user=user, recipe=recipe).exists():
            raise ValidationError(
                {'error': 'Этот рецепт уже добавлен'}
            )
        return data

    def to_representation(self, instance):
        context = {'request': self.context.get('request')}
        return RecipeDetailSerializer(instance.recipe, context=context).data


class ShoppingCartSerializer(FavoriteSerializer):
    """Сериализатор добавления/удаления рецепта в список покупок."""
    class Meta(FavoriteSerializer.Meta):
        model = ShoppingCart
