from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (IngredientViewSet, RecipeViewSet,
                    TagViewSet)
from users.views import CustomUserViewSet


app_name = 'api'

# Создание роутера для API-представлений
router_v1 = DefaultRouter()
router_v1.register('users', CustomUserViewSet, basename='users')
router_v1.register('tags', TagViewSet, basename='tags')
router_v1.register('ingredients', IngredientViewSet, basename='ingredients')
router_v1.register('recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    # Включение URL-маршрутов, созданных роутером
    path('', include(router_v1.urls)),
    # Включение URL-маршрутов для авторизации с помощью djoser
    path('auth/', include('djoser.urls.authtoken')),
]
