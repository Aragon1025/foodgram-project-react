import json
import os

from django.conf import settings
from django.core.management import BaseCommand
from recipes.models import Ingredient


def iter_json(file_path: str):
    with open(os.path.dirname(settings.BASE_DIR) + file_path, 'r',
              encoding="utf8") as inp_f:
        reader = json.load(inp_f)
        for row in reader:
            yield row


class Command(BaseCommand):
    def handle(self, *args, **options):
        reader = iter_json('/data/ingredients.json')
        for row in reader:
            ingredient = Ingredient(name=row['name'],
                                    measurement_unit=row['measurement_unit'])
            ingredient.save()
        self.stdout.write(self.style.SUCCESS('Successfully add ingredients'))