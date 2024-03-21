from django.conf import settings
from django.db.models import F
from django.core.validators import MaxValueValidator, MinValueValidator
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import (
    SerializerMethodField,
)
from rest_framework.validators import UniqueTogetherValidator
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField

from recipes.models import (
    Favorite, Ingredient, IngredientAmount, Recipe,
    ShoppingCart, Tag
)
from users.models import User


class CustomUserCreateSerializer(UserCreateSerializer): 
    """
    Сериализатор для создания пользователя.
    """
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = (
            *User.REQUIRED_FIELDS,
            User.USERNAME_FIELD,
            'password'
        )


class CustomUserSerializer(UserSerializer):
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

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return obj.subscriber.filter(user=user).exists()


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
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    name = serializers.ReadOnlyField(source='ingredient.name') 
    measurement_unit = serializers.ReadOnlyField(source='ingredient.measurement_unit') 
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
        if obj.image:
            return obj.image.url
        return None

    def get_is_favorited(self, obj):
        """
        Проверяет, добавлен ли рецепт в избранное.
        """
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return Favorite.objects.filter(user=user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        """
        Проверяет, добавлен ли рецепт в корзину покупок.
        """
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return user.shoppingcart_user.filter(recipe=obj).exists()


class AddIngredientToRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    
    class Meta:
        model = IngredientAmount
        fields = ('id', 'amount')

class CreateRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    author = CustomUserSerializer(read_only=True)
    ingredients = AddIngredientToRecipeSerializer(many=True)
    cooking_time = serializers.IntegerField(
        validators=[
            MinValueValidator(settings.VALUE_RECIPE_MIN),
            MaxValueValidator(settings.VALUE_RECIPE_MAX)
        ]
    )
    tags = serializers.SlugRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        slug_field='id'
    )

    class Meta:
        model = Recipe
        fields = [
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
        ]

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        if ingredients:
            ingredient_ids = set()
            for ingredient in ingredients:
                ingredient_id = ingredient.get('id')
                if ingredient_id in ingredient_ids:
                    raise serializers.ValidationError('Ингредиент уже есть!')
                ingredient_ids.add(ingredient_id)
        return data

    def create_bulk(self, recipe, ingredients_data):
        ingredients = [
            IngredientAmount(
                ingredient=ingredient['id'],
                recipe=recipe,
                amount=ingredient['amount']
            ) for ingredient in ingredients_data
        ]
        IngredientAmount.objects.bulk_create(ingredients)

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        author_id = self.context['request'].user.id
        recipe = Recipe.objects.create(author_id=author_id, **validated_data)
        recipe.tags.set(tags_data)
        for ingredient_data in ingredients_data:
            ingredient = ingredient_data['id']
            amount = ingredient_data['amount']
            IngredientAmount.objects.create(recipe=recipe, ingredient=ingredient, amount=amount)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        instance.tags.clear()
        self.create_bulk(instance, ingredients_data)
        instance.tags.set(tags_data)
        return super().update(instance, validated_data)


class ShowRecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(
        read_only=True,
        many=True
    )
    image = Base64ImageField()
    author = CustomUserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField(
        'get_is_favorited'
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        'get_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = [
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
        ]

    def get_ingredients(self, recipe):
        ingredients = recipe.ingredients.values(
            'id', 'name', 'measurement_unit', amount=F('recipe__amount')
        )
        return ingredients

    def get_is_favorited(self, recipe):
        user = self.context['request'].user

        if user.is_anonymous:
            return False

        return user.favorite.filter(recipe=recipe).exists()

    def get_is_in_shopping_cart(self, recipe):
        user = self.context['request'].user

        if user.is_anonymous:
            return False

        return user.shoppingcart_user.filter(recipe=recipe).exists()


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
        return ShowRecipeSerializer(instance.recipe, context=context).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели ShoppingCart.
    """
    class Meta(FavoriteSerializer.Meta):
        model = ShoppingCart


class SubscriptionSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Подписок.
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
