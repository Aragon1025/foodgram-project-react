import os
from csv import reader

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from recipes.models import Ingredient

# Путь к папке с данными
DATA_ROOT = os.path.join(settings.BASE_DIR, 'data')

class Command(BaseCommand):
    # Описание команды
    help = 'Загружаем csv файл в базу данных'

    # Определение аргументов команды
    def add_arguments(self, parser):
        parser.add_argument('filename', default='ingredients.csv', nargs='?',
                            type=str)

    # Логика выполнения команды
    def handle(self, *args, **options):
        try:
            # Открываем файл CSV и считываем его содержимое
            with open(os.path.join(DATA_ROOT, options['filename']), 'r',
                      encoding='utf-8') as file_csv:
                data = reader(file_csv)
                # Проходимся по строкам файла и создаем или обновляем записи об ингредиентах
                for name, measurement_unit in data:
                    Ingredient.objects.get_or_create(
                        name=name,
                        measurement_unit=measurement_unit
                    )
        except FileNotFoundError:
            # Обработка исключения, если файл не найден
            msg = 'Добавьте файл c данными в директорию data'
            raise CommandError(msg)
