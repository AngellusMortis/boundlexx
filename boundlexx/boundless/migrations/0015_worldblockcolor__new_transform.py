# Generated by Django 3.0.9 on 2020-08-04 01:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('boundless', '0014_auto_20200803_1930'),
    ]

    operations = [
        migrations.AddField(
            model_name='worldblockcolor',
            name='_new_transform',
            field=models.NullBooleanField(),
        ),
    ]
