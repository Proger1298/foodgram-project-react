from django.contrib.auth import authenticate
from django.db.models import F
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from drf_base64.fields import Base64ImageField

from recipes.models import (
    Recipe,
    Tag,
    Ingredient,
    RecipeIngredient,
    RecipeFavorite,
    ShoppingCart,
)
from users.models import User, Subscription


class UserSerializer(serializers.ModelSerializer):
    is_subscribed= serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
            'is_subscribed'
        )
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Subscription.objects.filter(user=user, author=obj).exists()

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=254, required=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        user = authenticate(
            username = attrs.get('email'),
            password = attrs.get('password')
        )
        if user is None:
            raise serializers.ValidationError(
                'Неверные почта или пароль! Попробуйте снова.'
            )
        return attrs


class PasswordSerializer(serializers.ModelSerializer):
    new_password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )
    current_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        fields = ('new_password', 'current_password')
        model = User

    def validate_current_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError(
                'Текущий пароль введен неверно!'
            )
        return value


class SubscriptionRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField(
        max_length=None,
        use_url=True
    )

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('recipes', 'recipes_count')
        read_only_fields = (
            'email',
            'username',
            'first_name',
            'last_name',
        )
        extra_kwargs = {
            'password': {'read_only': True}
        }
        
    def validate(self, attrs):
        user = self.context['request'].user
        author_id = (
            self.context.get(
                'request'
            ).parser_context.get('kwargs').get('pk')
        )
        if Subscription.objects.filter(
            user=user,
            author_id=author_id
        ).exists():
            raise serializers.ValidationError(
                'Вы уже подписаны на данного автора!'
            )
        if user.id == author_id:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя!'
            )
        return attrs

    def get_recipes(self, obj):
        limit = self.context.get('request').query_params.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit:
            recipes = obj.recipes.all()[:int(limit)]
        return SubscriptionRecipeSerializer(recipes, many=True).data
    
    def get_recipes_count(self, obj):
        return obj.recipes.count()

class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug',)


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class GetRecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(
        read_only=True
    )
    tags = TagSerializer(
        read_only=True,
        many=True
    )
    ingredients = serializers.SerializerMethodField()
    image = Base64ImageField(
        max_length=None,
        use_url=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')
        
    def get_ingredients(self, obj):
        return obj.ingredients.values(
            'id',
            'name',
            'measurement_unit',
            amount=F('recipe__amount')
        )

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return RecipeFavorite.objects.filter(
            user=user, recipe=obj
        ).exists()
    
    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=user, recipe=obj
        ).exists()


class IngredientsRecipePostSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(
        write_only=True
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class PostRecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(
        read_only=True
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    ingredients = IngredientsRecipePostSerializer(
        many=True
    )
    image = Base64ImageField(
        required=False,
        allow_null=True,
        max_length=None,
        use_url=True
    )

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'name', 'image', 'text', 'cooking_time')
        
    def validate_tags(self, tags):
        current_tags = []
        for tag in tags:
            if not Tag.objects.filter(id=tag.id).exists():
                raise serializers.ValidationError(
                    'Указанного тега не существует! Измените теги.'
                )
            if tag in current_tags:
                raise serializers.ValidationError(
                    'Теги повторяются! Измените теги.'
                )
            current_tags.append(tag)
        return tags

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise serializers.ValidationError(
                'Без ингредиентов ничего не приготовишь :('
            )
        current_ingredients_ids = []
        for ingredient in ingredients:
            ingredient_id = ingredient.get('id')
            if not Ingredient.objects.filter(id=ingredient_id).exists():
                raise serializers.ValidationError(
                    'Указанного ингредиента не существует! '
                    'Измените состав рецепта.'
                )
            if ingredient_id in current_ingredients_ids:
                raise serializers.ValidationError(
                    'Ингредиенты повтоярются! Измените состав рецепта.'
                )
            if ingredient.get('amount') < 1:
                raise serializers.ValidationError(
                    'Маловато будет на готовку! Измените кол-во ингредиента.'
                )
            current_ingredients_ids.append(ingredient_id)
        return ingredients
    
    def validate_cooking_time(self, cooking_time):
        if cooking_time < 1:
            raise serializers.ValidationError(
                'Меньше, чем за минуту ничего не приготовишь :(')
        return cooking_time

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        for ingredient in ingredients:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient_id=ingredient.get('id'),
                amount=ingredient.get('amount'), 
            )
        return recipe
    
    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance = super().update(instance, validated_data)
        instance.tags.clear()
        instance.tags.set(tags)
        instance.ingredients.clear()
        for ingredient in ingredients:
            RecipeIngredient.objects.create(
                recipe=instance,
                ingredient_id=ingredient.get('id'),
                amount=ingredient.get('amount'), 
            )
        instance.save()
        return instance

    def to_representation(self, instance):
        return GetRecipeSerializer(
            instance,
            context={'request': self.context.get('request')}
        ).data
