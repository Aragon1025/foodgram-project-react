# Generated by Django 3.2 on 2024-04-12 18:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_auto_20240321_2315'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='is_subscribed',
            field=models.BooleanField(default=False, help_text='Подписаться', verbose_name='Подписка'),
        ),
        migrations.AlterField(
            model_name='user',
            name='password',
            field=models.CharField(max_length=128, verbose_name='password'),
        ),
    ]