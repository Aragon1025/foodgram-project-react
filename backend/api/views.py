from django.shortcuts import HttpResponse, get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, views, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from api.filters import IngredientSearchFilter, RecipesFilter
from api.pagination import CustomPagination
from api.permissions import IsAuthenticatedAuthorOrReadOnly
from api.serializers import (IngredientSerializer, RecipeReadsSerializer,
                             RecipeWritiSerializer, ShortRecipeSerializer,
                             SubscriptionSerializer, TagSerializer,
                             UserSerializer)
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
    """
    Представление для просмотра, создания, обновления и удаления рецептов.
    """
    queryset = Recipe.objects.all()
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipesFilter
    permission_classes = [IsAuthenticatedAuthorOrReadOnly]

    def perform_create(self, serializer):
        """
        Сохранение рецепта с указанием автора.
        """
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        """
        Определяет класс сериализатора в зависимости от метода запроса.
        """
        if self.request.method in ['GET']:
            return RecipeReadsSerializer
        return RecipeWritiSerializer

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk):
        """
        Добавляет или удаляет рецепт из избранного пользователя.
        """
        if request.method == 'POST':
            return self.add_obj(Favorite, request.user, pk)
        if request.method == 'DELETE':
            return self.delete_obj(Favorite, request.user, pk)
        return None

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk):
        """
        Добавляет или удаляет рецепт из корзины покупок пользователя.
        """
        if request.method == 'POST':
            return self.add_obj(ShoppingCart, request.user, pk)
        if request.method == 'DELETE':
            return self.delete_obj(ShoppingCart, request.user, pk)
        return None

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        """
        Генерирует и возвращает список ингредиентов для покупок в формате TXT.
        """
        ingredients = IngredientAmount.objects.filter(
            recipe__shoppingcart_recipe__user=request.user
        ).values_list(
            'ingredient__name', 'ingredient__measurement_unit',
            'amount'
        )
        shopping_list = generate_shopping_list(ingredients)
        response = HttpResponse(content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.txt"'
        )
        response.write(shopping_list)
        return response

    def add_obje(self, model, user, pk):
        """
        Добавляет модель (рецепт) к пользователю.
        """
        if model.objects.filter(user=user, recipe__id=pk).exists():
            return Response({
                'errors': 'Рецепт уже добавлен в список'
            }, status=status.HTTP_400_BAD_REQUEST)
        recipe = get_object_or_404(Recipe, id=pk)
        model.objects.create(user=user, recipe=recipe)
        serializer = ShortRecipeSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_obje(self, model, user, pk):
        """
        Удаляет объект модели (рецепт) к пользователю.
        """
        obj = model.objects.filter(user=user, recipe__id=pk)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({
            'errors': 'Рецепт удален ранее'
        }, status=status.HTTP_400_BAD_REQUEST)


class CustomUserViewSet(viewsets.ModelViewSet):
    """
    Удаляет объект модели (рецепт) у пользователя.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)


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


class SubscribeView(views.APIView):
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
