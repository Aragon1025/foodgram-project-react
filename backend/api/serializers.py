from django.conf import settings
from django.db.models import F
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import (
    SerializerMethodField,
)
from rest_framework.validators import UniqueTogetherValidator
from djoser.serializers import UserSerializer, UserCreateSerializer
from drf_extra_fields.fields import Base64ImageField

from recipes.models import (
    Favorite, Ingredient, IngredientAmount, Recipe,
    ShoppingCart, Tag
)
from users.models import User


User = get_user_model()


class CustomUserCreateSerializer(UserCreateSerializer):
    """
    Сериализатор для регистрации пользователей.
    """

    class Meta:
        model = User
        fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'password'
        )


class CustomUserSerializer(UserSerializer):
    """
    Сериализатор для управления пользователями.
    """
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'id', 'username', 'first_name', 'last_name', 'email',
            'is_subscribed'
        )
        model = User

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return (request
                and request.user.is_authenticated
                and obj.following.filter(
                    user=request.user
                ).exists())


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


class AddIngredientToRecipeSerializer(serializers.ModelSerializer):
    """
    Ингредиенты.
    """
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = IngredientAmount
        fields = ('id', 'amount')


class CreateRecipeSerializer(serializers.ModelSerializer):
    """
    Серелизатор создания рецепта.
    """
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
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get('cooking_time', instance.cooking_time)
        instance.save()

        tags_data = validated_data.pop('tags')
        instance.tags.set(tags_data)

        ingredients_data = validated_data.pop('ingredients', [])
        if ingredients_data:
            instance.ingredients.clear()
            self.create_bulk(instance, ingredients_data)

        return instance


class ShowRecipeSerializer(serializers.ModelSerializer):
    """
    Серелизатор представления рецепта.
    """
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
    Сериализатор для модели Избранный.
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


class RecipeForFollowersSerializer(serializers.ModelSerializer):
    """
    Сериализатор для отображения рецептов в подписке.
    """
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class SubscriptionSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Подписок.
    """
    recipes_count = SerializerMethodField()
    recipes = RecipeForFollowersSerializer(
        many=True,
        read_only=True
    )

    def get_recipes_count(self, obj):
        """
        Функция для получения количества рецептов пользователя.
        """
        recipes = Recipe.objects.filter(
            author=obj.id
        )
        return recipes.count()

    class Meta(CustomUserSerializer.Meta):
        fields = (
            CustomUserSerializer.Meta.fields
            + ('recipes', 'recipes_count',)
        )
        read_only_fields = (
            'email',
            'username',
            'first_name',
            'last_name',
        )
