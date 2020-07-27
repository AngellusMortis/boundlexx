# Generated by Django 3.0.8 on 2020-07-27 00:19

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('boundless', '0008_worldpoll_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='world',
            name='region',
            field=models.CharField(choices=[('use', 'US East'), ('usw', 'US West'), ('ecu', 'EU Central'), ('aus', 'Australia'), ('creative', 'Creative')], max_length=16, verbose_name='Server Region'),
        ),
        migrations.AlterField(
            model_name='world',
            name='region',
            field=models.CharField(choices=[('use', 'US East'), ('usw', 'US West'), ('euc', 'EU Central'), ('aus', 'Australia'), ('creative', 'Creative')], max_length=16, verbose_name='Server Region'),
        ),
        migrations.AlterField(
            model_name='world',
            name='description',
            field=models.CharField(max_length=32, verbose_name='Description'),
        ),
        migrations.AddField(
            model_name='world',
            name='assignment',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='world',
            name='creative',
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.AddField(
            model_name='world',
            name='owner',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='world',
            name='locked',
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.AddField(
            model_name='world',
            name='number_of_regions',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='world',
            name='public',
            field=models.BooleanField(db_index=True, default=True),
        ),
        migrations.AlterField(
            model_name='world',
            name='address',
            field=models.CharField(blank=True, max_length=128, null=True, verbose_name='Server Address'),
        ),
        migrations.AlterField(
            model_name='world',
            name='api_url',
            field=models.URLField(blank=True, null=True, verbose_name='API URL'),
        ),
        migrations.AlterField(
            model_name='world',
            name='chunks_url',
            field=models.URLField(blank=True, null=True, verbose_name='Chunks URL'),
        ),
        migrations.AlterField(
            model_name='world',
            name='ip_address',
            field=models.GenericIPAddressField(blank=True, null=True, verbose_name='Server IP Address'),
        ),
        migrations.AlterField(
            model_name='world',
            name='planets_url',
            field=models.URLField(blank=True, null=True, verbose_name='Planets URL'),
        ),
        migrations.AlterField(
            model_name='world',
            name='websocket_url',
            field=models.URLField(blank=True, null=True, verbose_name='Websocket URL'),
        ),
        migrations.AlterField(
            model_name='world',
            name='tier',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Placid (1)'), (1, 'Temperate (2)'), (2, 'Rugged (3)'), (3, 'Inhospitable (4)'), (4, 'Turbulent (5)'), (5, 'Fierce (6)'), (6, 'Savage (7)'), (7, 'Brutal (8)')], verbose_name='Tier'),
        ),
        migrations.AlterField(
            model_name='world',
            name='world_type',
            field=models.CharField(choices=[('LUSH', 'Lush'), ('METAL', 'Metal'), ('COAL', 'Coal'), ('CORROSIVE', 'Corrosive'), ('SHOCK', 'Shock'), ('BLAST', 'Blast'), ('TOXIC', 'Toxic'), ('CHILL', 'Chill'), ('BURN', 'Burn'), ('UMBRIS', 'Umbris'), ('RIFT', 'Rift'), ('BLINK', 'Blink')], max_length=9, verbose_name='World Type'),
        ),
    ]