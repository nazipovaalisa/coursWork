# Generated by Django 4.0.3 on 2022-05-19 07:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('CinemaApp', '0005_order_cart'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ticket',
            name='available',
        ),
    ]
