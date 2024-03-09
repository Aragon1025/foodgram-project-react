from django.contrib import admin

from .models import Favorite, Ingredient, IngredientAmount, Recipe, ShoppingCart, Tag


class IngredientAmountInline(admin.TabularInline):
    model = IngredientAmount


class IngredientAmountAdmin(admin.ModelAdmin):
    # Настройки для административной панели для модели IngredientAmount
    list_display = ('pk', 'recipe', 'ingredient', 'amount')  # Отображаемые поля в списке
    search_fields = ('recipe__name', 'ingredient__name')  # Поля для поиска
    # Определение класса административной панели для тегов

class TagAdmin(admin.ModelAdmin):
    # Настройки для административной панели для модели Tag
    list_display = ('pk', 'name', 'color', 'slug')  # Отображаемые поля в списке
    list_editable = ('name', 'color', 'slug')  # Поля, которые можно редактировать прямо из списка
    search_fields = ('name',)  # Поля для поиска
    empty_value_display = '-пусто-'  # Текст для пустых значений


class RecipeAdmin(admin.ModelAdmin):
    # Настройки для административной панели для модели Recipe
    list_display = ('name', 'author', 'count_favorites')  # Отображаемые поля в списке
    list_filter = ('author', 'name', 'tags')  # Фильтры для списка
    search_fields = ('author__username', 'name', 'tags__name')  # Поля для поиска
    inlines = [IngredientAmountInline]  # Добавляем инлайн для отображения IngredientAmount
    empty_value_display = '-пусто-'  # Текст для пустых значений

    def count_favorites(self, obj):
        return obj.favorite_recipe.count()  # Метод для отображения количества избранных рецептов


class IngredientAdmin(admin.ModelAdmin):
    # Настройки для административной панели для модели Ingredient
    list_display = ('pk', 'name', 'measurement_unit')  # Отображаемые поля в списке
    search_fields = ('name',)  # Поля для поиска
    list_filter = ('name',)  # Фильтры для списка
    empty_value_display = '-пусто-'  # Текст для пустых значений


class FavoriteAdmin(admin.ModelAdmin):
    # Настройки для административной панели для модели Favorite
    list_display = ('pk', 'user', 'recipe')  # Отображаемые поля в списке
    search_fields = ('user__username', 'recipe__name')  # Поля для поиска


class ShoppingCartAdmin(admin.ModelAdmin):
    # Настройки для административной панели для модели ShoppingCart
    list_display = ('pk', 'user', 'recipe')  # Отображаемые поля в списке
    search_fields = ('user__username', 'recipe__name')  # Поля для поиска

# Регистрируем модели и их административные классы в административной панели Django

admin.site.register(Tag, TagAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(IngredientAmount, IngredientAmountAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
