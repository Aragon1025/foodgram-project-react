from django.core.management.base import BaseCommand
from django.db.models import Count

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Удаление дубликатов ингердиентов из БД'

    def handle(self, *args, **options):
        duplicates = (
            Ingredient.objects.values('name')
            .annotate(name_count=Count('name'))
            .filter(name_count__gt=1)
        )

        for item in duplicates:
            name = item['name']
            ingredients = Ingredient.objects.filter(name=name)
            first_ingredient = ingredients.first()
            ingredients.exclude(pk=first_ingredient.pk).delete()

        self.stdout.write(self.style.SUCCESS('Дубликаты успешно удалены'))
