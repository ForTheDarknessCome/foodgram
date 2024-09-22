from rest_framework import serializers
from cooking.models import Recipe, Tag, Ingredient, RecipeIngredient, Favorite, ShoppingCart
from utils.fields import Base64ImageField



# class RecipeIngredientSerializer(serializers.ModelSerializer):
#     id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all(), source='ingredient')

#     class Meta:
#         model = RecipeIngredient
#         fields = ('id', 'amount')

#     def validate_ingredient_id(self, value):
#         if not Ingredient.objects.filter(id=value.id).exists():
#             raise serializers.ValidationError("Этот ингредиент не существует.")
#         return value


# class RecipeSerializer(serializers.ModelSerializer):
#     image = Base64ImageField(required=True, allow_null=True,)
#     ingredients = RecipeIngredientSerializer(many=True)
#     tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)

#     class Meta:
#         model = Recipe
#         fields = ('name', 'text', 'image', 'cooking_time', 'tags', 'ingredients', 'author', 'id')
#         read_only_fields = ('author',)

#     def create(self, validated_data):
#         ingredients_data = validated_data.pop('ingredients')
#         tags_data = validated_data.pop('tags')

#         # Создание рецепта
#         recipe = Recipe.objects.create(**validated_data)

#         # Создание ингредиентов
#         for ingredient_data in ingredients_data:
#             ingredient_id = ingredient_data.pop('id')  # Извлечение ID ингредиента
#             RecipeIngredient.objects.create(recipe=recipe, ingredient_id=ingredient_id, **ingredient_data)

#         recipe.tags.set(tags_data)

#         return recipe
class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=True, allow_null=True)
    ingredients = RecipeIngredientSerializer(many=True)
    # tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    tags = TagSerializer(many=True, required=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited', 'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time')
        read_only_fields = ('author',)

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return Favorite.objects.filter(user=user, recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return ShoppingCart.objects.filter(user=user, recipe=obj).exists()
        return False

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')

        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags_data)

        for ingredient_data in ingredients_data:
            ingredient_id = ingredient_data['id']
            amount = ingredient_data['amount']

            ingredient, _ = Ingredient.objects.get_or_create(id=ingredient_id)

            RecipeIngredient.objects.create(recipe=recipe, ingredient=ingredient, amount=amount)

        return recipe

    def partial_update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.image = validated_data.get('image', instance.image)
        instance.cooking_time = validated_data.get('cooking_time', instance.cooking_time)

        if 'tags' in validated_data:
            tags_data = validated_data.pop('tags')
            instance.tags.set(tags_data)

        if 'ingredients' in validated_data:
            ingredients_data = validated_data.pop('ingredients')
            instance.recipeingredient_set.all().delete()
            for ingredient_data in ingredients_data:
                ingredient_id = ingredient_data['id']
                amount = ingredient_data['amount']
                ingredient, _ = Ingredient.objects.get_or_create(id=ingredient_id)
                RecipeIngredient.objects.create(recipe=instance, ingredient=ingredient, amount=amount)

        instance.save()
        return instance


class RecipeDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
