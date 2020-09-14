# Generated by Django 3.0.10 on 2020-09-14 19:51

import django.contrib.postgres.indexes
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    replaces = [('boundless', '0027_skills_recipes'), ('boundless', '0028_auto_20200913_1239'), ('boundless', '0029_localizedstringtext__plain_text')]

    dependencies = [
        ('boundless', '0026_auto_20200912_1701'),
    ]

    operations = [
        migrations.CreateModel(
            name='LocalizedString',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('string_id', models.CharField(max_length=64, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('gameobj_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='boundless.GameObj')),
                ('heat', models.PositiveSmallIntegerField()),
                ('craft_xp', models.PositiveSmallIntegerField()),
                ('machine', models.CharField(choices=[('COMPACTOR', 'COMPACTOR'), ('CRAFTING_TABLE', 'CRAFTING_TABLE'), ('DYE_MAKER', 'DYE_MAKER'), ('EXTRACTOR', 'EXTRACTOR'), ('FURNACE', 'FURNACE'), ('MIXER', 'MIXER'), ('REFINERY', 'REFINERY'), ('WORKBENCH', 'WORKBENCH')], max_length=16, null=True)),
                ('machine_level', models.CharField(blank=True, choices=[('', ''), ('Standard', 'Standard'), ('Powered', 'Powered'), ('Overdriven', 'Overdriven'), ('Supercharged', 'Supercharged')], max_length=16)),
                ('power', models.PositiveIntegerField()),
                ('group_name', models.CharField(max_length=32)),
                ('knowledge_unlock_level', models.PositiveIntegerField()),
            ],
            options={
                'abstract': False,
                'base_manager_name': 'objects',
            },
            bases=('boundless.gameobj',),
        ),
        migrations.CreateModel(
            name='RecipeGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32)),
                ('display_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='boundless.LocalizedString')),
            ],
        ),
        migrations.AddField(
            model_name='item',
            name='mint_value',
            field=models.FloatField(default=0, verbose_name='Chrysominter Value'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='item',
            name='name',
            field=models.CharField(default='', max_length=64, verbose_name='Name'),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='SkillGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('skill_type', models.CharField(choices=[('Attributes', 'Attributes'), ('Basic', 'Basic'), ('Epic', 'Epic')], max_length=16)),
                ('name', models.CharField(max_length=16)),
                ('unlock_level', models.PositiveIntegerField()),
                ('display_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='boundless.LocalizedString')),
            ],
        ),
        migrations.CreateModel(
            name='Skill',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number_unlocks', models.PositiveIntegerField(help_text='How many times this skill can be unlocked')),
                ('cost', models.PositiveIntegerField()),
                ('name', models.CharField(max_length=64)),
                ('order', models.PositiveIntegerField()),
                ('category', models.CharField(max_length=32)),
                ('link_type', models.CharField(choices=[('None', 'None'), ('Left', 'Left'), ('Right', 'Right')], max_length=8)),
                ('bundle_prefix', models.CharField(max_length=128)),
                ('affected_by_other_skills', models.BooleanField()),
                ('description', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='boundless.LocalizedString')),
                ('display_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='boundless.LocalizedString')),
            ],
        ),
        migrations.CreateModel(
            name='RecipeTint',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='boundless.Item')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tint_from', to='boundless.Recipe')),
            ],
        ),
        migrations.CreateModel(
            name='RecipeRequirement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level', models.PositiveSmallIntegerField()),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='boundless.Recipe')),
                ('skill', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='boundless.Skill')),
            ],
        ),
        migrations.CreateModel(
            name='RecipeLevel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level', models.PositiveIntegerField(choices=[(0, 'Single'), (1, 'Bulk'), (2, 'Mass')])),
                ('wear', models.PositiveIntegerField()),
                ('spark', models.PositiveIntegerField()),
                ('duration', models.PositiveIntegerField()),
                ('output_quantity', models.PositiveIntegerField()),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='boundless.Recipe')),
            ],
        ),
        migrations.CreateModel(
            name='RecipeInput',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('count', models.PositiveSmallIntegerField()),
                ('group', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='boundless.RecipeGroup')),
                ('item', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='boundless.Item')),
                ('recipe_level', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='boundless.RecipeLevel')),
            ],
        ),
        migrations.CreateModel(
            name='RecipeGroupMember',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='boundless.RecipeGroup')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='boundless.Item')),
            ],
        ),
        migrations.AddField(
            model_name='recipe',
            name='output',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='boundless.Item'),
        ),
        migrations.CreateModel(
            name='LocalizedStringText',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lang', models.CharField(max_length=16, verbose_name='Language')),
                ('text', models.TextField()),
                ('string', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='boundless.LocalizedString')),
            ],
        ),
        migrations.AddIndex(
            model_name='localizedstringtext',
            index=django.contrib.postgres.indexes.GinIndex(fields=['string'], name='boundless_l_string__91275e_gin'),
        ),
        migrations.AlterField(
            model_name='item',
            name='mint_value',
            field=models.FloatField(blank=True, null=True, verbose_name='Chrysominter Value'),
        ),
        migrations.AlterField(
            model_name='localizedstring',
            name='string_id',
            field=models.CharField(max_length=128, unique=True),
        ),
        migrations.AddField(
            model_name='item',
            name='description',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='boundless.LocalizedString'),
        ),
        migrations.AddField(
            model_name='item',
            name='list_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='boundless.LocalizedString'),
        ),
        migrations.AddField(
            model_name='skill',
            name='group',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='boundless.SkillGroup'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='localizedstringtext',
            name='string',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='strings', to='boundless.LocalizedString'),
        ),
        migrations.AlterField(
            model_name='skill',
            name='name',
            field=models.CharField(max_length=64, unique=True),
        ),
        migrations.AlterField(
            model_name='skillgroup',
            name='name',
            field=models.CharField(max_length=16, unique=True),
        ),
        migrations.RemoveField(
            model_name='recipetint',
            name='item',
        ),
        migrations.RemoveField(
            model_name='recipetint',
            name='recipe',
        ),
        migrations.RemoveField(
            model_name='recipeinput',
            name='recipe_level',
        ),
        migrations.RemoveField(
            model_name='recipelevel',
            name='recipe',
        ),
        migrations.RemoveField(
            model_name='reciperequirement',
            name='recipe',
        ),
        migrations.AddField(
            model_name='recipe',
            name='can_hand_craft',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='recipe',
            name='tints',
            field=models.ManyToManyField(related_name='_recipe_tints_+', to='boundless.Item'),
        ),
        migrations.AddField(
            model_name='recipegroup',
            name='members',
            field=models.ManyToManyField(to='boundless.Item'),
        ),
        migrations.DeleteModel(
            name='RecipeGroupMember',
        ),
        migrations.DeleteModel(
            name='RecipeTint',
        ),
        migrations.AddField(
            model_name='recipe',
            name='requirements',
            field=models.ManyToManyField(to='boundless.RecipeRequirement'),
        ),
        migrations.AddField(
            model_name='recipe',
            name='levels',
            field=models.ManyToManyField(to='boundless.RecipeLevel'),
        ),
        migrations.AddField(
            model_name='recipelevel',
            name='inputs',
            field=models.ManyToManyField(to='boundless.RecipeInput'),
        ),
        migrations.RemoveIndex(
            model_name='localizedstringtext',
            name='boundless_l_string__91275e_gin',
        ),
        migrations.AddIndex(
            model_name='localizedstringtext',
            index=django.contrib.postgres.indexes.GinIndex(fields=['text'], name='boundless_l_text_aa0532_gin'),
        ),
        migrations.AddIndex(
            model_name='skill',
            index=django.contrib.postgres.indexes.GinIndex(fields=['name'], name='boundless_s_name_a7d57d_gin'),
        ),
        migrations.AddIndex(
            model_name='skillgroup',
            index=django.contrib.postgres.indexes.GinIndex(fields=['name'], name='boundless_s_name_7fe673_gin'),
        ),
        migrations.AddField(
            model_name='localizedstringtext',
            name='_plain_text',
            field=models.TextField(blank=True, null=True),
        ),
    ]
