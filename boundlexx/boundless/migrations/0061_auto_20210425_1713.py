# Generated by Django 3.1.8 on 2021-04-25 21:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('boundless', '0060_world_last_updated'),
    ]

    operations = [
        migrations.AlterField(
            model_name='settlement',
            name='html_name',
            field=models.CharField(blank=True, max_length=1024, null=True),
        ),
        migrations.AlterField(
            model_name='settlement',
            name='text_name',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
    ]