from django.urls import include, path
from rest_framework import routers

from api.views import (IngredientViewSet, RecipeViewSet, TagViewSet,
                       UserViewSet, login, logout)

app_name = 'api'

router = routers.DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
auth_urls = [
    path('login/', login),
    path('logout/', logout),
]

urlpatterns = [
    path('', include(router.urls)),
    path('auth/token/', include(auth_urls)),
]
