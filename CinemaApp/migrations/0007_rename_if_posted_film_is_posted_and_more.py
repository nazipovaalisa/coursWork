# Generated by Django 4.0.3 on 2022-05-23 14:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('CinemaApp', '0006_remove_ticket_available'),
    ]

    operations = [
        migrations.RenameField(
            model_name='film',
            old_name='if_posted',
            new_name='is_posted',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='is_active',
        ),
    ]
