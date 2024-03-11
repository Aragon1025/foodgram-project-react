from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter
from recipes.models import Tag, Recipe
from users.models import User


class IngredientSearchFilter(SearchFilter):
    """
    Фильтр поиска ингредиентов по имени.
    """
    search_param = 'name'


class RecipesFilter(filters.FilterSet):
    """
    Набор фильтров для рецептов.
    """
    tags = filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug',
        label='Теги',
        help_text='Фильтр рецептов по тегам.'
    )
    author = filters.ModelChoiceFilter(
        queryset=User.objects.all(),
        label='Автор',
        help_text='Фильтр рецептов по автору.'
    )
    is_favorited = filters.BooleanFilter(
        method='get_is_favorited',
        label='В избранном',
        help_text='Фильтр рецептов, которые находятся в избранном.'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart',
        label='В корзине',
        help_text='Фильтр рецептов, которые находятся в корзине покупок.'
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')

    def get_is_favorited(self, queryset, name, value):
        """
        Фильтр рецептов, которые добавлены в избранное.
        """
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(favorite_recipe__user=user)
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        """
        Фильтр рецептов, которые добавлены в корзину покупок.
        """
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(shoppingcart_recipe__user=user)
        return queryset
