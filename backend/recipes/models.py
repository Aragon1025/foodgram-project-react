from colorfield.fields import ColorField
from django.contrib.auth import get_user_model
from django.core import validators
from django.conf import settings
from django.db import models

User = get_user_model()


MIN_COOKING_TIME = 1
MAX_COOKING_TIME = 32000
MIN_INGREDIENT_AMOUNT = 1
MAX_INGREDIENT_AMOUNT = 32000


class Ingredient(models.Model):
    """Модель Ингредиента."""
    name = models.CharField(
        max_length=settings.MAX_LENGTH_TEXT,
        verbose_name='Название',
    )
    measurement_unit = models.CharField(
        max_length=settings.MAX_LENGTH_TEXT,
        verbose_name='Единицы измерения',
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        """Название Ингредиента."""
        return self.name


class Tag(models.Model):
    """Модель Тэга."""
    name = models.CharField(
        max_length=settings.MAX_LENGTH_TEXT,
        unique=True,
        verbose_name='Название тэга',
    )
    color = ColorField(
        verbose_name='Цвет',
        format='hex',
        max_length=settings.MAX_LENGTH_HEX,
    )
    slug = models.SlugField(
        max_length=settings.MAX_LENGTH_TEXT,
        unique=True,
        verbose_name='Слаг',
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        """Имя Тега."""
        return self.name


class Recipe(models.Model):
    """Модель Рецепта."""
    name = models.CharField(
        max_length=settings.MAX_LENGTH_TEXT,
        verbose_name='Название',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта',
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Тэги рецепта',
    )
    ingredients = models.ManyToManyField(
        'Ingredient',
        through='IngredientAmount',
        verbose_name='Ингредиенты в рецепте',
        related_name='recipes',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='Дата',
    )
    image = models.ImageField(
        upload_to='recipes/',
        null=True,
        blank=True,
        verbose_name='Картинка рецепта',
    )
    text = models.TextField(
        verbose_name='Описание рецепта',
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=[
            validators.MinValueValidator(
                MIN_COOKING_TIME,
                message=f'Минимальное время {MIN_COOKING_TIME} минута!',
            ),
            validators.MaxValueValidator(
                MAX_COOKING_TIME,
                message=f'Максимальное время {MAX_COOKING_TIME} минут!',
            ),
        ],
        verbose_name='Время приготовления (в минутах)',
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        """Название Рецепта."""
        return self.name


class IngredientAmount(models.Model):
    """Модель количества ингредиентов."""
    ingredient = models.ForeignKey(
        to=Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиенты в рецепте',
        related_name='recipe',
    )
    recipe = models.ForeignKey(
        to=Recipe,
        on_delete=models.CASCADE,
        verbose_name='В каком рецепте ',
        related_name='ingredient',
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество ингредиента',
        default=1,
        validators=(
            validators.MinValueValidator(
                MIN_INGREDIENT_AMOUNT,
                message=f'Минимальное количество {MIN_INGREDIENT_AMOUNT}',
            ),
            validators.MaxValueValidator(
                MAX_INGREDIENT_AMOUNT,
                message=f'Максимальное количество {MAX_INGREDIENT_AMOUNT}',
            ),
        ),
    )

    class Meta:
        ordering = ['amount']
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'
        constraints = [
            models.UniqueConstraint(fields=['ingredient', 'recipe'],
                                    name='unique_ingredients_recipe')
        ]

    def __str__(self):
        """Рецепт - Ингредиент в нём."""
        return f'{self.recipe} - {self.ingredient}'


class Favorite(models.Model):
    """Модель избранного рецепта."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта',
        related_name='favorite',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite',
        verbose_name='Рецепт автора',
    )
    when_added = models.DateTimeField(
        auto_now_add=True,
        editable=False,
        verbose_name='Дата добавления'
    )

    class Meta:
        ordering = ['recipe']
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_name_favorite'
            )
        ]

    def __str__(self):
        """Автор - Рецепт."""
        return f'{self.user} - {self.recipe}'


class ShoppingCart(models.Model):
    """Модель списка покупок."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shoppingcart_user',
        verbose_name='Пользователь сайта',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shoppingcart_recipe',
        verbose_name='Рецепт в корзине пользователя',
    )

    class Meta:
        verbose_name = 'Cписок покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_cart_user'
            )
        ]

    def __str__(self):
        """Список покупок пользователя."""
        return f'{self.user} - {self.recipe}'
