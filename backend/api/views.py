from django.shortcuts import HttpResponse, get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from api.filters import IngredientSearchFilter, RecipesFilter
from api.pagination import CustomPagination
from api.permissions import IsAuthenticatedAuthorOrReadOnly
from api.serializers import (IngredientSerializer, ShoppingCartSerializer,
                             CreateRecipeSerializer, ShowRecipeSerializer,
                             SubscriptionSerializer, TagSerializer,
                             UserSerializer, FavoriteSerializer)
from recipes.models import (Favorite, Ingredient, IngredientAmount, Recipe,
                            ShoppingCart, Tag)
from users.models import Follow, User


def generate_shopping_list(value_list):
    """
    Генерирует текстовый список ингредиентов для покупки.

    Args:
    value_list (list): Список значений ингредиентов.

    Returns:
    str: Текстовый список ингредиентов.
    """
    shopping_list = {}
    for item in value_list:
        name, measurement_unit, amount = item
        if name not in shopping_list:
            shopping_list[name] = {
                'measurement_unit': measurement_unit,
                'amount': amount
            }
        else:
            shopping_list[name]['amount'] += amount

    formatted_list = []
    for index, (name, data) in enumerate(shopping_list.items(), start=1):
        formatted_list.append(
            f"{index}. {name} ({data['measurement_unit']}) - {data['amount']}"
        )

    return "\n".join(formatted_list)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Представление для просмотра тегов.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Представление для просмотра ингредиентов.
    """
    queryset = Ingredient.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = IngredientSerializer
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('^name',)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = [IsAuthenticatedAuthorOrReadOnly]
    filterset_class = RecipesFilter
    filter_backends = (DjangoFilterBackend,)
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.request.method == 'POST' or self.request.method == 'PATCH':
            return CreateRecipeSerializer
        return ShowRecipeSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context

    @action(
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def generate_shopping_list(self, request):
        """
        Генерирует список покупок на основе рецептов пользователя.
        Формат TXT
        """
        recipes = self.filter_queryset(self.get_queryset())
        shopping_list = {}
        for recipe in recipes:
            ingredients = IngredientAmount.objects.filter(recipe=recipe)
            for ingredient in ingredients:
                name = ingredient.ingredient.name
                measurement_unit = ingredient.ingredient.measurement_unit
                amount = ingredient.amount
                if name not in shopping_list:
                    shopping_list[name] = {
                        'measurement_unit': measurement_unit,
                        'amount': amount
                    }
                else:
                    shopping_list[name]['amount'] += amount

        formatted_list = []
        for index, (name, data) in enumerate(shopping_list.items(), start=1):
            formatted_list.append(
                f"{index}. {name} ({data['measurement_unit']}) - {data['amount']}"
            )

        shopping_list_text = "\n".join(formatted_list)
        response = HttpResponse(shopping_list_text, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="shopping_list.txt"'
        return response


class CustomUserViewSet(viewsets.ModelViewSet):
    """
    Удаляет объект модели (рецепт) у пользователя.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)


class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class SubscriptionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Представление для просмотра, создания, обновления и удаления пользователей.
    """
    serializer_class = SubscriptionSerializer
    pagination_class = CustomPagination
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend,)

    def get_queryset(self):
        return User.objects.filter(following__user=self.request.user)


class SubscribeView(APIView):
    """
    Представление для подписки на пользователей и отписки от них.
    """
    serializer_class = SubscriptionSerializer
    pagination_class = CustomPagination
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        """
        Добавляет подписку на пользователя.
        """
        user_id = self.kwargs.get('user_id')

        if user_id == request.user.id:
            return Response(
                {'Запрещено подписываться на себя'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if Follow.objects.filter(
                user=request.user,
                author_id=user_id
        ).exists():
            return Response(
                {'Вы уже подписаны на автора'},
                status=status.HTTP_400_BAD_REQUEST
            )

        author = get_object_or_404(User, id=user_id)
        Follow.objects.create(
            user=request.user,
            author_id=user_id
        )

        return Response(
            self.serializer_class(author, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )

    def delete(self, request, *args, **kwargs):
        """
        Удаляет подписку на пользователя.
        """
        user_id = self.kwargs.get('user_id')
        get_object_or_404(User, id=user_id)
        subscription = request.user.following.filter(author_id=user_id)
        if subscription:
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'error': 'Вы не подписаны на пользователя'},
            status=status.HTTP_400_BAD_REQUEST
        )


class FavoriteView(APIView):
    """
    Обработчик для добавления и удаления рецептов в избранное.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, recipe_id):
        user = request.user
        recipe = get_object_or_404(Recipe, id=recipe_id)
        if Favorite.objects.filter(user=user, recipe=recipe).exists():
            return Response({'error': 'Рецепт уже в избранном!'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = FavoriteSerializer(data={'user': user.id, 'recipe': recipe_id}, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, recipe_id):
        user = request.user
        recipe = get_object_or_404(Recipe, id=recipe_id)
        favorite = get_object_or_404(Favorite, user=user, recipe=recipe)
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShoppingCartView(APIView):
    """
    Обработчик для добавления и удаления рецептов в список покупок.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, recipe_id):
        user = request.user
        recipe = get_object_or_404(Recipe, id=recipe_id)
        if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
            return Response({'error': 'Рецепт уже в списке покупок!'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = ShoppingCartSerializer(data={'user': user.id, 'recipe': recipe_id})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, recipe_id):
        user = request.user
        recipe = get_object_or_404(Recipe, id=recipe_id)
        shopping_cart = get_object_or_404(ShoppingCart, user=user, recipe=recipe)
        shopping_cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
