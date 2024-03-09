from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CustomUserViewSet, IngredientViewSet, RecipeViewSet,
                    SubscribeView, SubscriptionViewSet, TagViewSet)

app_name = 'api'

# Создание роутера для API-представлений
router_v1 = DefaultRouter()
router_v1.register('users', CustomUserViewSet, basename='users')
router_v1.register('recipes', RecipeViewSet, basename='recipes')
router_v1.register('tags', TagViewSet, basename='tags')
router_v1.register('ingredients', IngredientViewSet, basename='ingredients')

# Определение URL-маршрутов
urlpatterns = [
    # Маршрут для списка подписок пользователя
    path(
        'users/subscriptions/',
        SubscriptionViewSet.as_view({'get': 'list'}),
        name='subscriptions'
    ),
    # Маршрут для подписки на пользователя
    path(
        'users/<int:user_id>/subscribe/',
        SubscribeView.as_view(),
        name='subscribe'
    ),
    # Включение URL-маршрутов, созданных роутером
    path('', include(router_v1.urls)),
    # Включение URL-маршрутов для аутентификации с помощью djoser
    path('', include('djoser.urls')),
    # Включение URL-маршрутов для авторизации с помощью djoser
    path('auth/', include('djoser.urls.authtoken')),
]
