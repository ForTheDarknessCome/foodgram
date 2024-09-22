from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        max_length=24,
        verbose_name='Название'
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='Слаг'
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['name']

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    UNIT_CHOICES = [
        ('g', 'Граммы'),
        ('kg', 'Килограммы'),
        ('ml', 'Миллилитры'),
        ('l', 'Литры'),
        ('pcs', 'Штуки'),
    ]

    name = models.CharField(
        max_length=128,
        verbose_name='Название ингредиента'
    )
    measurement_unit = models.CharField(
        max_length=3,
        choices=UNIT_CHOICES,
        verbose_name='Единица измерения'
    )


class Recipe(models.Model):
    name = models.CharField(
        max_length=256,
        verbose_name='Название'
    )
    author = models.ForeignKey(
        User,
        related_name='recipes',
        on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to='recipes/images/')
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления (в минутах)',
        help_text='Укажите время приготовления в минутах.',
        validators=[MinValueValidator(1)]
    )
    text = models.TextField(blank=False)
    tags = models.ManyToManyField(
        'Tag',
        related_name='recipes'
    )
    ingredients = models.ManyToManyField(
        'Ingredient',
        through='RecipeIngredient',
        related_name='recipes'
    )

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='recipe_ingredients')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name='recipe_ingredients')
    amount = models.PositiveSmallIntegerField(
        default=1,
        help_text="Введите количество ингредиента.",
        verbose_name="Количество ингредиента",
        validators=[
            MinValueValidator(1),
            MaxValueValidator(999)
        ]
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['recipe', 'ingredient'], name='unique_recipe_ingredient')
        ]


class BaseRelation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=('Пользователь'))
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, verbose_name=('Рецепт'))

    class Meta:
        abstract = True


class Favorite(BaseRelation):
    """Модель для хранения избранных рецептов пользователя."""

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'], name='unique_favorite_user_recipe')
        ]
        verbose_name = ('Любимый рецепт')
        verbose_name_plural = ('Любимые рецептыэ')


class ShoppingCart(BaseRelation):
    """Модель для хранения рецептов в корзине покупок пользователя."""

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'], name='unique_cart_user_recipe')
        ]
        verbose_name = ('Элемент списка покупок')
        verbose_name_plural = ('Элементы списка покупок')
