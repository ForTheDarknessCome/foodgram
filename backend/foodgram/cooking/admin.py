from django.contrib import admin
from cooking.models import Tag, Recipe, Ingredient, Favorite, ShoppingCart, RecipeIngredient
from django.utils.html import mark_safe
import base64


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1
    fields = ('ingredient', 'amount')
    verbose_name = 'Ингредиент'
    verbose_name_plural = 'Ингредиенты'


class TagAdmin(admin.ModelAdmin):
    model = Tag
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)


class RecipeAdmin(admin.ModelAdmin):
    model = Recipe
    list_display = ('name', 'author', 'cooking_time', 'pub_date', 'display_image')
    list_filter = ('author', 'tags')
    search_fields = ('name', 'author__username')
    inlines = [RecipeIngredientInline]
    filter_horizontal = ('tags',)
    ordering = ('-pub_date',)

    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'author', 'image', 'cooking_time', 'text'),
        }),
        ('Дополнительно', {
            'fields': ('tags',),
            'description': 'Выберите теги для рецепта.',
        }),
    )

    def display_image(self, obj):
        optimized_image = obj.get_optimized_image()
        optimized_image.seek(0)
        img_data = base64.b64encode(optimized_image.read()).decode()

        return mark_safe(f'<img src="data:image/jpeg;base64,{img_data}" style="width: 150px; height: 150px;" />')

    display_image.short_description = 'Image'


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    list_filter = ('user',)
    search_fields = ('user__username', 'recipe__name')


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    list_filter = ('user',)
    search_fields = ('user__username', 'recipe__name')


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
