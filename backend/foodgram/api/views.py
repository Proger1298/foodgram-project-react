import io

from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import SAFE_METHODS, AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from api.filters import IngredientFilter, RecipeFilter
from api.pagination import PageLimitPagination
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (GetRecipeSerializer, IngredientSerializer,
                             LoginSerializer, PasswordSerializer,
                             PostRecipeSerializer,
                             SubscriptionRecipeSerializer,
                             SubscriptionSerializer, TagSerializer,
                             UserSerializer)
from recipes.models import (Ingredient, Recipe, RecipeFavorite, ShoppingCart,
                            Tag)
from users.models import Subscription, User

FONT_SIZE = 24  # Размер шрифта для пдф в пунктах
TEXT_INDENT = 15  # Отступ для текста для пдф, в миллиметрах


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = get_object_or_404(
        User,
        email=serializer.validated_data.get('email')
    )
    auth_token = Token.objects.get_or_create(user=user)[0]
    return Response(
        {'auth_token': f'{str(auth_token.key)}'},
        status=status.HTTP_201_CREATED
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated, ])
def logout(request):
    Token.objects.get(user=request.user).delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = PageLimitPagination
    permission_classes = (AllowAny, )

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(IsAuthenticated, )
    )
    def me(self, request):
        user = self.request.user
        return Response(
            self.get_serializer(user).data, status=status.HTTP_200_OK
        )

    @action(
        detail=False,
        methods=['post'],
        permission_classes=(IsAuthenticated, )
    )
    def set_password(self, request):
        user = self.request.user
        serializer = PasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        user.set_password(serializer.validated_data.get('new_password'))
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated, )
    )
    def subscribe(self, request, pk):
        user = self.request.user
        author = get_object_or_404(User, id=pk)
        if self.request.method == 'POST':
            serializer = SubscriptionSerializer(
                author, data=request.data, context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            Subscription.objects.create(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if self.request.method == 'DELETE':
            get_object_or_404(Subscription, user=user, author=author).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(IsAuthenticated, )
    )
    def subscriptions(self, request):
        subscriptions = Subscription.objects.filter(user=request.user)
        serializer = SubscriptionSerializer(
            subscriptions,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.select_related('author')
    pagination_class = PageLimitPagination
    permission_classes = (IsAuthorOrReadOnly, )
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return GetRecipeSerializer
        return PostRecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def include(self, model, user, recipe_id):
        recipe = get_object_or_404(Recipe, id=recipe_id)
        recipe_in_cart = model.objects.filter(
            user=user,
            recipe=recipe
        )
        if recipe_in_cart.exists():
            return Response(
                {'errors': 'Вы уже добавили данный рецепт!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        model.objects.create(user=user, recipe=recipe)
        return Response(
            SubscriptionRecipeSerializer(recipe).data,
            status=status.HTTP_201_CREATED
        )

    def exclude(self, model, user, recipe_id):
        recipe = get_object_or_404(Recipe, id=recipe_id)
        recipe_in_cart = model.objects.filter(
            user=user,
            recipe=recipe
        )
        if recipe_in_cart.exists():
            recipe_in_cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': 'Вы уже удалили данный рецепт!'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated, )
    )
    def favorite(self, request, pk):
        print(self.request.method)
        if self.request.method == 'POST':
            return self.include(RecipeFavorite, request.user, pk)
        return self.exclude(RecipeFavorite, request.user, pk)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated, )
    )
    def shopping_cart(self, request, pk):
        if self.request.method == 'POST':
            return self.include(ShoppingCart, request.user, pk)
        return self.exclude(ShoppingCart, request.user, pk)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        buffer = io.BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=A4, bottomup=0)
        pdfmetrics.registerFont(TTFont('FreeSans', 'FreeSans.ttf'))
        pdf.setFont('FreeSans', FONT_SIZE)
        text_obj = pdf.beginText()
        text_obj.setTextOrigin(TEXT_INDENT * mm, TEXT_INDENT * mm)
        shopping_cart = Ingredient.objects.filter(
            recipe__recipe__in_carts__user=request.user
        ).values(
            'name',
            'measurement_unit'
        ).annotate(amount=Sum('recipe__amount')).order_by()
        lines = []
        lines.append("--- Список покупок Foodgram ---")
        lines.append("")
        ingredient_number = 1
        for ingredient in shopping_cart:
            name = ingredient.get('name')
            amount = ingredient.get('amount')
            measurement_unit = ingredient.get('measurement_unit')
            lines.append(
                f'{ingredient_number}) '
                f'{name} - '
                f'{amount}, '
                f'{measurement_unit}'
            )
            ingredient_number += 1
        lines.append("")
        lines.append("--- Список покупок Foodgram ---")
        for line in lines:
            text_obj.textLine(line)
        pdf.drawText(text_obj)
        pdf.showPage()
        pdf.save()
        buffer.seek(0)
        return FileResponse(
            buffer, as_attachment=True, filename='foodgram_shopping_cart.pdf'
        )


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend, )
    filterset_class = IngredientFilter
