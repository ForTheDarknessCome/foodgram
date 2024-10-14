import base64

from django.contrib import admin
from django.utils.html import mark_safe

from cooking.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag
)


class RecipeIngredientInline(admin.TabularInline):
    """Inline для редактирования ингредиентов рецепта в админке."""

    model = RecipeIngredient
    extra = 1
    fields = ('ingredient', 'amount')
    verbose_name = 'Ингредиент'
    verbose_name_plural = 'Ингредиенты'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Админка для управления тегами рецептов."""

    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Админка для управления ингредиентами."""

    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Админка для управления рецептами."""

    list_display = (
        'name',
        'author',
        'cooking_time',
        'pub_date',
        'display_image',
    )
    list_filter = ('author', 'tags')
    search_fields = ('name', 'author__username')
    inlines = [RecipeIngredientInline]
    filter_horizontal = ('tags',)
    ordering = ('-pub_date',)

    fieldsets = (
        (
            'Основная информация',
            {
                'fields': ('name', 'author', 'image', 'cooking_time', 'text'),
            },
        ),
        (
            'Дополнительно',
            {
                'fields': ('tags',),
                'description': 'Выберите теги для рецепта.',
            },
        ),
    )

    def display_image(self, obj):
        """Отображает изображение рецепта в админке."""
        optimized_image = obj.get_optimized_image()
        optimized_image.seek(0)
        img_data = base64.b64encode(optimized_image.read()).decode()

        return mark_safe(
            f'<img src="data:image/jpeg;base64,{img_data}" '
            f'style="width: 150px; height: 150px;" />'
        )

    display_image.short_description = 'Image'


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Админка для управления избранными рецептами пользователей."""

    list_display = ('user', 'recipe')
    list_filter = ('user',)
    search_fields = ('user__username', 'recipe__name')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Админка для управления корзиной покупок пользователей."""

    list_display = ('user', 'recipe')
    list_filter = ('user',)
    search_fields = ('user__username', 'recipe__name')
