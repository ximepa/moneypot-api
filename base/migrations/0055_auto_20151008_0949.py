# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0054_itemchunk_cell'),
    ]

    operations = [
        migrations.CreateModel(
            name='FixPlaceMerge',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('old_place_sav_id', models.PositiveIntegerField(null=True, blank=True)),
                ('old_place_sav_name', models.CharField(max_length=100, null=True, blank=True)),
                ('new_place', models.ForeignKey(related_name='new_places', verbose_name='new place', to='base.Place')),
                ('old_place', models.ForeignKey(related_name='old_places', on_delete=django.db.models.deletion.SET_NULL, verbose_name='old place', to='base.Place', null=True)),
            ],
        ),
        migrations.AlterField(
            model_name='fixcategorymerge',
            name='old_category',
            field=models.ForeignKey(related_name='old_categoriess', on_delete=django.db.models.deletion.SET_NULL, verbose_name='old item category', to='base.ItemCategory', null=True),
        ),
    ]
