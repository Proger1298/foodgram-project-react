import django_filters

from recipes.models import Ingredient, Recipe, Tag
from users.models import User


class RecipeFilter(django_filters.FilterSet):
    is_favorited = django_filters.NumberFilter(
        label='В избранных',
        method='filter_is_favorited'
    )
    author = django_filters.ModelChoiceFilter(
        queryset=User.objects.all()
    )
    is_in_shopping_cart = django_filters.NumberFilter(
        label='В списке покупок',
        method='filter_is_in_shopping_cart'
    )
    tags = django_filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()

    )

    class Meta:
        model = Recipe
        fields = ('is_favorited', 'author', 'is_in_shopping_cart', 'tags')

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if value and not user.is_anonymous:
            return queryset.filter(in_favorites__user=user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if value and not user.is_anonymous:
            return queryset.filter(in_carts__user=user)
        return queryset


class IngredientFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name', )
