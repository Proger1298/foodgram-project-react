from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from users.models import User

MIN_COOKING_TIME = 1  # Минимальное время приготовления рецепта в минутах
MAX_COOKING_TIME = 600  # Максимальное время приготовления рецепта в минутах
MIN_INGREDIENTS_AMOUNT = 1  # Минимальное количество ингридиентов в рецепте
MAX_INGREDIENTS_AMOUNT = 2000  # Максимальное количество ингридиентов в рецепте


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name='Название'
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единицы измерения'
    )

    class Meta:
        ordering = ('name', )
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name} - {self.measurement_unit}'


class Tag(models.Model):
    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Название'
    )
    color = models.CharField(
        max_length=7,
        unique=True,
        verbose_name='Цвет'
    )
    slug = models.SlugField(
        unique=True,
        max_length=200,
        verbose_name='Уникальный slug'
    )

    class Meta:
        ordering = ('id', )
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name='Автор рецепта',
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Название рецепта'
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        null=True,
        blank=True,
        default=None
    )
    text = models.TextField(
        verbose_name='Описание рецепта',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        blank=False,
        related_name='recipes',
        verbose_name='Ингредиенты',
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги',
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=(
            MinValueValidator(MIN_COOKING_TIME),
            MaxValueValidator(MAX_COOKING_TIME)
        )
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )

    class Meta:
        ordering = ('-pub_date', )
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return f'{self.author.username}: {self.name}'


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='В каких рецептах',
        related_name='ingredient',
        on_delete=models.CASCADE
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Связанные ингредиенты',
        related_name='recipe',
        on_delete=models.CASCADE
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество ингредиента',
        validators=(
            MinValueValidator(MIN_INGREDIENTS_AMOUNT),
            MaxValueValidator(MAX_INGREDIENTS_AMOUNT)
        )
    )

    class Meta:
        ordering = ('-id', )
        verbose_name = 'Рецепт - Ингредиент'
        verbose_name_plural = 'Рецепт - Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_ingredient')]

    def __str__(self):
        return f'{self.recipe.name} - {self.ingredient.name}, {self.amount}'


class RecipeFavorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='in_favorites',
        verbose_name='Понравившиеся рецепты'
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite'
            )
        ]

    def __str__(self):
        return f'{self.user.username} - {self.recipe.name}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_carts',
        verbose_name='Владелец списка'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='in_carts',
        verbose_name='Рецепты в корзине'
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Рецепт в корзине'
        verbose_name_plural = 'Рецепты в корзинах'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_recipe_in_cart'
            )
        ]

    def __str__(self):
        return f'{self.user.username} - {self.recipe.name}'
