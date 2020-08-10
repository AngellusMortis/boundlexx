# Generated by Django 3.0.9 on 2020-08-10 03:16

from django.db import migrations, models

def update_world_type(apps, schema_editor):
    World = apps.get_model("boundless", "World")

    for world in World.objects.filter(world_type="UMBRIS"):
        world.world_type = "DARKMATTER"
        world.save()


def revert_world_type(apps, schema_editor):
    World = apps.get_model("boundless", "World")

    for world in World.objects.filter(world_type="DARKMATTER"):
        world.world_type = "UMBRIS"
        world.save()


class Migration(migrations.Migration):

    dependencies = [
        ('boundless', '0017_auto_20200809_2312'),
    ]

    operations = [
        migrations.RunPython(update_world_type, revert_world_type),
        migrations.AlterField(
            model_name='world',
            name='world_type',
            field=models.CharField(choices=[('LUSH', 'Lush'), ('METAL', 'Metal'), ('COAL', 'Coal'), ('CORROSIVE', 'Corrosive'), ('SHOCK', 'Shock'), ('BLAST', 'Blast'), ('TOXIC', 'Toxic'), ('CHILL', 'Chill'), ('BURN', 'Burn'), ('DARKMATTER', 'Umbris'), ('RIFT', 'Rift'), ('BLINK', 'Blink')], db_index=True, max_length=10, null=True, verbose_name='World Type'),
        ),
    ]
