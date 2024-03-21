# Generated by Django 3.2 on 2024-03-21 17:31

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0005_auto_20240321_2009'),
    ]

    operations = [
        migrations.AddField(
            model_name='favorite',
            name='when_added',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='Дата добавления'),
            preserve_default=False,
        ),
    ]