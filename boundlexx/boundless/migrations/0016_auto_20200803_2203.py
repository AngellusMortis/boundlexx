# Generated by Django 3.0.9 on 2020-08-04 02:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('boundless', '0015_worldblockcolor__new_transform'),
    ]

    operations = [
        migrations.RenameField(
            model_name='worldblockcolor',
            old_name='_new_transform',
            new_name='_exist_via_transform',
        ),
    ]
