# Generated by Django 3.0.10 on 2020-09-23 13:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('boundless', '0042_forumimage_checksum'),
    ]

    operations = [
        migrations.AddField(
            model_name='forumimage',
            name='shortcut_url',
            field=models.CharField(default=None, max_length=64),
            preserve_default=False,
        ),
    ]