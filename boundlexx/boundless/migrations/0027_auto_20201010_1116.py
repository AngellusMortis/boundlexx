# Generated by Django 3.1.2 on 2020-10-10 15:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('boundless', '0026_auto_20201009_1742'),
    ]

    operations = [
        migrations.RenameField(
            model_name='resourcecount',
            old_name='_average_per_chunk',
            new_name='average_per_chunk',
        ),
    ]
