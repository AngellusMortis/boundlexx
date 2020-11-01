# Generated by Django 3.1.2 on 2020-11-01 15:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('boundless', '0037_auto_20201031_1311'),
    ]

    operations = [
        migrations.CreateModel(
            name='ResourceData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_embedded', models.BooleanField()),
                ('exo_only', models.BooleanField(default=False)),
                ('max_tier', models.PositiveSmallIntegerField(choices=[(0, 'T1 - Placid'), (1, 'T2 - Temperate'), (2, 'T3 - Rugged'), (3, 'T4 - Inhospitable'), (4, 'T5 - Turbulent'), (5, 'T6 - Fierce'), (6, 'T7 - Savage'), (7, 'T8 - Brutal')], help_text='Max tier of world to be found on. Starts at 0.', verbose_name='Max Tier')),
                ('min_tier', models.PositiveSmallIntegerField(choices=[(0, 'T1 - Placid'), (1, 'T2 - Temperate'), (2, 'T3 - Rugged'), (3, 'T4 - Inhospitable'), (4, 'T5 - Turbulent'), (5, 'T6 - Fierce'), (6, 'T7 - Savage'), (7, 'T8 - Brutal')], help_text='Min tier of world to be found on. Starts at 0.', verbose_name='Min Tier')),
                ('best_max_tier', models.PositiveSmallIntegerField(choices=[(0, 'T1 - Placid'), (1, 'T2 - Temperate'), (2, 'T3 - Rugged'), (3, 'T4 - Inhospitable'), (4, 'T5 - Turbulent'), (5, 'T6 - Fierce'), (6, 'T7 - Savage'), (7, 'T8 - Brutal')], help_text='Max tier of world to be found on. Starts at 0.', verbose_name='Max Tier')),
                ('best_min_tier', models.PositiveSmallIntegerField(choices=[(0, 'T1 - Placid'), (1, 'T2 - Temperate'), (2, 'T3 - Rugged'), (3, 'T4 - Inhospitable'), (4, 'T5 - Turbulent'), (5, 'T6 - Fierce'), (6, 'T7 - Savage'), (7, 'T8 - Brutal')], help_text='Min tier of world to be found on. Starts at 0.', verbose_name='Min Tier')),
                ('shape', models.PositiveSmallIntegerField()),
                ('size_max', models.PositiveSmallIntegerField()),
                ('size_min', models.PositiveSmallIntegerField()),
                ('altitude_max', models.PositiveSmallIntegerField()),
                ('altitude_min', models.PositiveSmallIntegerField()),
                ('distance_max', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('distance_min', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('cave_weighting', models.FloatField()),
                ('size_skew_to_min', models.FloatField()),
                ('blocks_above_max', models.PositiveSmallIntegerField()),
                ('blocks_above_min', models.PositiveSmallIntegerField()),
                ('liquid_above_max', models.PositiveSmallIntegerField()),
                ('liquid_above_min', models.PositiveSmallIntegerField()),
                ('noise_frequency', models.FloatField(blank=True, null=True)),
                ('noise_threshold', models.FloatField(blank=True, null=True)),
                ('three_d_weighting', models.FloatField()),
                ('surface_weighting', models.FloatField()),
                ('altitude_best_lower', models.PositiveSmallIntegerField()),
                ('altitude_best_upper', models.PositiveSmallIntegerField()),
                ('distance_best_lower', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('distance_best_upper', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('blocks_above_best_lower', models.PositiveSmallIntegerField()),
                ('blocks_above_best_upper', models.PositiveSmallIntegerField()),
                ('liquid_above_best_upper', models.PositiveSmallIntegerField()),
                ('liquid_above_best_lower', models.PositiveSmallIntegerField()),
            ],
        ),
        migrations.AddField(
            model_name='item',
            name='build_xp',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='item',
            name='is_resource',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='item',
            name='mine_xp',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='item',
            name='prestige',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='item',
            name='max_stack',
            field=models.PositiveSmallIntegerField(default=100),
        ),
        migrations.CreateModel(
            name='ResourceDataBestWorld',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('world_type', models.CharField(choices=[('LUSH', 'Lush'), ('METAL', 'Metal'), ('COAL', 'Coal'), ('CORROSIVE', 'Corrosive'), ('SHOCK', 'Shock'), ('BLAST', 'Blast'), ('TOXIC', 'Toxic'), ('CHILL', 'Chill'), ('BURN', 'Burn'), ('DARKMATTER', 'Umbris'), ('RIFT', 'Rift'), ('BLINK', 'Blink')], max_length=10, verbose_name='World Type')),
                ('data', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='boundless.resourcedata')),
            ],
        ),
        migrations.AddField(
            model_name='resourcedata',
            name='item',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='resource_data', to='boundless.item'),
        ),
        migrations.AddField(
            model_name='resourcedata',
            name='liquid_favorite',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='boundless.item'),
        ),
        migrations.AddField(
            model_name='resourcedata',
            name='liquid_second_favorite',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='boundless.item'),
        ),
        migrations.AddField(
            model_name='resourcedata',
            name='surface_favorite',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='boundless.item'),
        ),
        migrations.AddField(
            model_name='resourcedata',
            name='surface_second_favorite',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='boundless.item'),
        ),
        migrations.CreateModel(
            name='Liquid',
            fields=[
                ('gameobj_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='boundless.gameobj')),
                ('name', models.CharField(max_length=64, unique=True, verbose_name='Name')),
                ('block_item', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='boundless.item')),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('boundless.gameobj',),
        ),
    ]
