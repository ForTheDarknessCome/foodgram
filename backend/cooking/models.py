from io import BytesIO

from PIL import Image as PilImage

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from utils.constants import (
    LENGTH_INGREDIENT_NAME,
    LENGTH_RECIPE_NAME,
    LENGTH_SLUG,
    LENGTH_TAG_NAME,
    MAX_SLICE,
    MEASUREMENT_UNIT_LENGTH,
)

User = get_user_model()


class Tag(models.Model):
    """Модель для тегов, используемых в рецептах."""

    name = models.CharField(
        max_length=LENGTH_TAG_NAME, verbose_name='Название'
    )
    slug = models.SlugField(
        max_length=LENGTH_SLUG, unique=True, verbose_name='Слаг'
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель для хранения ингредиентов и их единиц измерения."""

    name = models.CharField(
        max_length=LENGTH_INGREDIENT_NAME, verbose_name='Название'
    )
    measurement_unit = models.CharField(
        max_length=MEASUREMENT_UNIT_LENGTH, verbose_name='Единица измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
    """Модель для хранения информации о рецепте, включая ингредиенты и теги."""

    name = models.CharField(
        max_length=LENGTH_RECIPE_NAME, verbose_name='Название'
    )
    author = models.ForeignKey(
        User,
        related_name='recipes',
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта',
    )
    image = models.ImageField(
        upload_to='recipes/images/', verbose_name='Изображение рецепта'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления (в минутах)',
        help_text='Укажите время приготовления в минутах.',
        validators=[MinValueValidator(1)],
    )
    text = models.TextField(blank=False, verbose_name='Описание рецепта')
    tags = models.ManyToManyField(
        'Tag', related_name='recipes', verbose_name='Теги'
    )
    ingredients = models.ManyToManyField(
        'Ingredient',
        through='RecipeIngredient',
        related_name='recipes',
        verbose_name='Ингредиенты',
    )
    pub_date = models.DateTimeField(
        auto_now=True, verbose_name='Дата публикации'
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def clean(self):
        """Проверяет, что рецепт имеет хотя бы один тег и ингредиент."""
        super().clean()
        if not self.tags.exists():
            raise ValidationError(
                {'tags': 'Необходимо указать хотя бы один тег.'}
            )

        if not self.ingredients.exists():
            raise ValidationError(
                {'ingredients': 'Необходимо указать хотя бы один ингредиент.'}
            )

    def get_optimized_image(self):
        """Возвращает оптимизированное изображение рецепта."""
        image = PilImage.open(self.image)
        image = image.convert('RGB')
        image.thumbnail((300, 300))

        thumbnail_io = BytesIO()
        image.save(thumbnail_io, format='JPEG', quality=85)
        return ContentFile(thumbnail_io.getvalue(), name=self.image.name)

    def __str__(self):
        return f'{self.name[:MAX_SLICE]}'


class RecipeIngredient(models.Model):
    """Модель для связи рецепта с ингредиентами и их количеством."""

    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='recipe_ingredients'
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, related_name='recipe_ingredients'
    )
    amount = models.PositiveSmallIntegerField(
        default=1,
        help_text='Введите количество ингредиента.',
        verbose_name="Количество ингредиента",
        validators=[MinValueValidator(1), MaxValueValidator(999)],
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient',
            )
        ]

    def __str__(self):
        return (
            f'{self.recipe}: {self.ingredient.name},'
            f' {self.amount}, {self.ingredient.measurement_unit}'
        )


class Favorite(models.Model):
    """Модель для хранения избранных рецептов пользователя."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='favorites',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепты',
        related_name='favorites',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_favorite_user_recipe'
            )
        ]
        verbose_name = 'Любимый рецепт'
        verbose_name_plural = 'Любимые рецепты'

    def __str__(self):
        return f'{self.recipe} в избранном у пользователя {self.user}'


class ShoppingCart(models.Model):
    """Модель для хранения рецептов в корзине покупок пользователя."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='shopping_carts',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепты',
        related_name='shopping_carts',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_cart_user_recipe'
            )
        ]
        verbose_name = 'Элемент списка покупок'
        verbose_name_plural = 'Элементы списка покупок'

    def __str__(self):
        return f'{self.recipe} в корзине у пользователя {self.user}'
