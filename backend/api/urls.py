from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CustomUserViewSet, CurrentUserView,
                    IngredientViewSet, RecipeViewSet,
                    SubscribeView, SubscriptionViewSet,
                    TagViewSet, FavoriteView, ShoppingCartView,)

app_name = 'api'

# Создание роутера для API-представлений
router_v1 = DefaultRouter()
router_v1.register('users', CustomUserViewSet, basename='users')
router_v1.register('tags', TagViewSet, basename='tags')
router_v1.register('ingredients', IngredientViewSet, basename='ingredients')
router_v1.register('recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path(
        'recipes/download_shopping_cart/',
        RecipeViewSet.as_view({'get': 'generate_shopping_list'}),
        name='download_shopping_cart',
    ),
    # Маршруты для добавления в избранное и корзину покупок
    path(
        'recipes/<int:recipe_id>/favorite/',
        FavoriteView.as_view(),
        name='favorite',
    ),
    path(
        'recipes/<int:recipe_id>/shopping_cart/',
        ShoppingCartView.as_view(),
        name='shopping_cart',
    ),

    # Маршрут для списка подписок пользователя
    path(
        'users/subscriptions/',
        SubscriptionViewSet.as_view({'get': 'list'}),
        name='subscriptions'
    ),

    # Маршрут для текущего пользователя
    path('users/me/', CurrentUserView.as_view(), name='current_user'),
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