# Generated by Django 4.0.3 on 2022-06-22 11:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CinemaApp', '0007_rename_if_posted_film_is_posted_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='seans',
            options={'ordering': ['date_seans', 'time_seans'], 'verbose_name': 'Сеанс', 'verbose_name_plural': 'Сеансы'},
        ),
        migrations.AddField(
            model_name='customer',
            name='is_active',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='cart',
            name='sum',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=9, null=True, verbose_name='Сумма'),
        ),
    ]
