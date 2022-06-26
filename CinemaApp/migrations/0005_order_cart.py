# Generated by Django 4.0.3 on 2022-05-18 17:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('CinemaApp', '0004_alter_ticket_bought'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='cart',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='related_cart', to='CinemaApp.cart', verbose_name='Корзина'),
        ),
    ]