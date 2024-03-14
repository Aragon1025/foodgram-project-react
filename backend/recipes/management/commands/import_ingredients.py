import json
from django.conf import settings
from django.core.management import BaseCommand
from recipes.models import Ingredient

class Command(BaseCommand):
    def handle(self, *args, **options):
        file_path = str(settings.BASE_DIR / 'data' / 'ingredients.json')
        with open(file_path, 'r', encoding="utf8") as inp_f:
            reader = json.load(inp_f)
            for row in reader:
                ingredient = Ingredient(name=row['name'], measurement_unit=row['measurement_unit'])
                ingredient.save()
        self.stdout.write(self.style.SUCCESS('Successfully added ingredients'))
