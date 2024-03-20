from django.core.exceptions import ValidationError
from django.db import transaction
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from rest_framework.validators import UniqueTogetherValidator
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField

from recipes.models import (
    Favorite, Ingredient, IngredientAmount, Recipe,
    ShoppingCart, Tag
)
from users.models import User

class UserSerializer(UserSerializer):
    """ Сериализатор пользователя """
    is_subscribed = SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', )

    def get_is_subscribed(self, obj):
        request = self.context['request']
        if request.user.is_anonymous:
            return False
        return obj.following.filter(user=request.user).exists()

class UserCreateSerializer(UserCreateSerializer):
    """ Сериализатор создания пользователя """

    is_subscribed = SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )


class TagSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели тега.
    """
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели ингредиента.
    """
    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientAmountSerializer(serializers.ModelSerializer):
    """ 
    Сериализатор для модели количества ингредиента. 
    """ 
    id = serializers.ReadOnlyField(source='ingredient.id') 
    name = serializers.ReadOnlyField(source='ingredient.name') 
    measurement_unit = serializers.ReadOnlyField( 
        source='ingredient.measurement_unit' 
    ) 
    amount = serializers.IntegerField(min_value=1, max_value=32000)

    class Meta:
        model = IngredientAmount
        fields = ('id', 'name', 'measurement_unit', 'amount')
        validators = [
            UniqueTogetherValidator(
                queryset=IngredientAmount.objects.all(),
                fields=['ingredient', 'recipe']
            )
        ]


class RecipeReadsSerializer(serializers.ModelSerializer):
    """
    Сериализатор для чтения рецепта.
    """
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientAmountSerializer(
        source='ingredientamount_set',
        many=True,
        read_only=True,
    )
    image = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_image(self, obj):
        """
        Получает URL изображения.
        """
        return obj.image.url

    def get_is_favorited(self, obj):
        """
        Проверяет, добавлен ли рецепт в избранное.
        """
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return user.favorite_recipe.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        """
        Проверяет, добавлен ли рецепт в корзину покупок.
        """
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return user.shoppingcart_recipe.filter(recipe=obj).exists()


class RecipeWritiSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания и обновления рецепта.
    """
    image = Base64ImageField()
    tags = TagSerializer(read_only=True, many=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientAmountSerializer(
        source='ingredientamount_set',
        many=True,
        read_only=True,
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def validate_cooking_time(self, value):
        """
        Проверяет, что время приготовления больше 0 и не превышает 32_000.
        """
        if value < 1:
            raise ValidationError('Минимальное время приготовления 1 минута!')
        elif value > 32_000:
            raise ValidationError('Максимальное время приготовления 32_000 минут!')
        return value

    def validate(self, data):
        """
        Проверяет наличие ингредиентов в рецепте и их уникальность.
        """
        ingredients = self.initial_data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError({
                'ingredients': 'Нужен хоть один ингредиент для рецепта'
            })
        
        ingredient_ids = set()
        for ingredient_item in ingredients:
            ingredient_id = ingredient_item.get('id')
            if ingredient_id in ingredient_ids:
                raise serializers.ValidationError('Ингридиенты должны быть уникальными')
            ingredient_ids.add(ingredient_id)

        return data

    @transaction.atomic
    def create(self, validated_data):
        """
        Создает рецепт с ингредиентами.
        """
        ingredients_data = validated_data.pop('ingredients')
        recipe = super().create(validated_data)
        IngredientAmount.objects.bulk_create([
            IngredientAmount(recipe=recipe, **ingredient_data)
            for ingredient_data in ingredients_data
        ])
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        """
        Обновляет рецепт с ингредиентами.
        """
        ingredients_data = validated_data.pop('ingredients', [])
        instance = super().update(instance, validated_data)
        instance.ingredientamount_set.all().delete()
        IngredientAmount.objects.bulk_create([
            IngredientAmount(recipe=instance, **ingredient_data)
            for ingredient_data in ingredients_data
        ])
        return instance

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeReadsSerializer(instance,
                                     context=context).data


class ShortRecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для краткого отображения рецепта.
    """
    image = serializers.SerializerMethodField()

    def get_image(self, obj):
        return obj.image.url

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time',)


class RecipeForUserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для рецептов пользователя.
    """
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FavoriteSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Favorite.
    """
    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

    def validate(self, data):
        """
        Проверяет, существует ли уже запись о рецепте в избранном.
        """
        user, recipe = data.get('user'), data.get('recipe')
        if Favorite.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError('Рецепт уже в избранном!')
        return data

    def to_representation(self, instance):
        """
        Преобразует экземпляр Favorite в JSON-представление.
        """
        request = self.context.get('request')
        context = {'request': request}
        return ShortRecipeSerializer(instance.recipe, context=context).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели ShoppingCart.
    """
    class Meta(FavoriteSerializer.Meta):
        model = ShoppingCart


class SubscriptionSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Subscription.
    """
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

    def validate(self, data):
        """
        Проверяет, подписан ли пользователь уже на автора.
        """
        user_id = data.get('author_id')
        request = self.context['request']

        if user_id == request.user.id:
            raise serializers.ValidationError(
                {'error': 'Запрещено подписываться на себя'}
            )

        if request.user.following.filter(author_id=user_id).exists():
            raise serializers.ValidationError(
                {'error': 'Вы уже подписаны на автора'}
            )
        return data

    def get_recipes_count(self, obj):
        """
        Получает количество рецептов пользователя.
        """
        return obj.recipes.count()

    def get_recipes(self, obj):
        """
        Получает список рецептов пользователя.
        """
        request = self.context.get('request')
        recipes = obj.recipes.all()
        
        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        return RecipeForUserSerializer(recipes, many=True).data
