# Generated by Django 3.2 on 2021-06-12 23:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('boundless', '0002_alter_world_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='color',
            name='base',
            field=models.CharField(blank=True, choices=[('AZURE', 'Azure'), ('CERULEAN', 'Cerulean'), ('COBALT', 'Cobalt'), ('BLUE', 'Blue'), ('LAVENDER', 'Lavender'), ('LILAC', 'Lilac'), ('MAGENTA', 'Magenta'), ('VIOLET', 'Violet'), ('BERRY', 'Berry'), ('FUCHSIA', 'Fuchsia'), ('CHERRY', 'Cherry'), ('RED', 'Red'), ('ROSE', 'Rose'), ('ORANGE', 'Orange'), ('SEPIA', 'Sepia'), ('TAUPE', 'Taupe'), ('MUSTARD', 'Mustard'), ('TAN', 'Tan'), ('YELLOW', 'Yellow'), ('LIME', 'Lime'), ('MOSS', 'Moss'), ('GREEN', 'Green'), ('MINT', 'Mint'), ('TEAL', 'Teal'), ('VIRIDIAN', 'Viridian'), ('TURQUOISE', 'Turquoise'), ('SLATE', 'Slate'), ('BLACK', 'BLACK')], max_length=16, null=True),
        ),
        migrations.AddField(
            model_name='color',
            name='group',
            field=models.CharField(blank=True, choices=[('BLUE', 'Blue'), ('VIOLET', 'Violet'), ('RED', 'Red'), ('ORANGE', 'Orange'), ('YELLOW', 'Yellow'), ('GREEN', 'Green'), ('BLACK', 'Black')], max_length=16, null=True),
        ),
        migrations.AddField(
            model_name='color',
            name='shade',
            field=models.CharField(blank=True, choices=[('BLACK', 'Black'), ('SHADOW', 'Shadow'), ('NIGHT', 'Night'), ('STRONG', 'Strong'), ('DARK', 'Dark'), ('DEEP', 'Deep'), ('HOT', 'Hot'), ('SILK', 'Silk'), ('OXIDE', 'Oxide'), ('PURE', 'Pure'), ('WARM', 'Warm'), ('SLATE', 'Slate'), ('RUST', 'Rust'), ('VIVID', 'Vidid'), ('LIGHT', 'Light'), ('PALE', 'Pale'), ('ASHEN', 'Ashen'), ('BRIGHT', 'Bright'), ('STARK', 'Stark'), ('COOL', 'Cool'), ('WEARY', 'Weary'), ('LUMINOUS', 'Luminous'), ('CRISP', 'Crisp'), ('COLD', 'Cold'), ('WHITE', 'White')], max_length=16, null=True),
        ),
    ]
