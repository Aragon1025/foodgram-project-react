# Generated by Django 3.2 on 2024-04-15 21:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0012_alter_recipe_tags'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='tags',
            field=models.ManyToManyField(related_name='recipes', to='recipes.Tag', verbose_name='Тэги'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='slug',
            field=models.SlugField(db_index=False, max_length=200, unique=True, verbose_name='Слаг'),
        ),
    ]
