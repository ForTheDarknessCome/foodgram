from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
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
    name = models.CharField(
        max_length=128,
        verbose_name='Название ингредиента'
    )
    measurement_unit = models.CharField(
        max_length=64,
        verbose_name='Единица измерения'
    )

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(
        max_length=256,
        verbose_name='Название'
    )
    author = models.ForeignKey(
        User,
        related_name='author',
        on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to='recipes/images/')
    cooking_time = models.PositiveIntegerField(
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
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(validators=[MinValueValidator(1)], verbose_name='Количество')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['recipe', 'ingredient'], name='unique_recipe_ingredient')
        ]
