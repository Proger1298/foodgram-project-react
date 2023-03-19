from django.contrib import admin

from recipes.models import (Ingredient, Recipe, RecipeFavorite,
                            RecipeIngredient, ShoppingCart, Tag)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'author',
        'in_favorites'
    )
    list_filter = ('author', 'name', 'tags')
    empty_value_display = '-empty-'

    def in_favorites(self, obj):
        return obj.in_favorites.count()


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name', )


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'color',
        'slug'
    )


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = (
        'recipe',
        'ingredient',
        'amount'
    )


@admin.register(RecipeFavorite)
class RecipeFavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
