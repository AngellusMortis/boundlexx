# Generated by Django 3.0.9 on 2020-08-03 23:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('boundless', '0013_auto_20200803_1301'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='world',
            name='closest_world',
        ),
        migrations.RemoveField(
            model_name='world',
            name='closest_world_distance',
        ),
        migrations.RemoveField(
            model_name='world',
            name='core_liquid',
        ),
        migrations.RemoveField(
            model_name='world',
            name='surface_liquid',
        ),
        migrations.AlterField(
            model_name='world',
            name='assignment',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='boundless.World'),
        ),
        migrations.CreateModel(
            name='WorldDistance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('distance', models.PositiveSmallIntegerField(verbose_name='Distance to work in blinksecs')),
                ('world_1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='boundless.World')),
                ('world_2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='boundless.World')),
            ],
        ),
    ]
