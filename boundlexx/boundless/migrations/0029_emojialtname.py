# Generated by Django 3.0.10 on 2020-09-16 12:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('boundless', '0028_auto_20200915_0931'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmojiAltName',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=32)),
                ('emoji', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='boundless.Emoji')),
            ],
        ),
    ]