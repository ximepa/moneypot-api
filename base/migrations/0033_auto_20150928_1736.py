# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0032_purchaseitem_cell'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cell',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=10)),
                ('place', models.ForeignKey(related_name='cells', verbose_name='source', to='base.Place')),
            ],
            options={
                'verbose_name': 'cell',
                'verbose_name_plural': 'cells',
            },
        ),
        migrations.CreateModel(
            name='CellItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('category', models.ForeignKey(related_name='cell_items', verbose_name='item category', to='base.ItemCategory')),
                ('cell', models.ForeignKey(verbose_name='cell', blank=True, to='base.Cell', null=True)),
                ('place', models.ForeignKey(related_name='cell_items', verbose_name='source', to='base.Place')),
                ('serial', models.ForeignKey(verbose_name='item serial', blank=True, to='base.ItemSerial', null=True)),
            ],
            options={
                'verbose_name': 'cell item',
                'verbose_name_plural': 'cell items',
            },
        ),
        migrations.AlterField(
            model_name='fixcategorymerge',
            name='new_category',
            field=models.ForeignKey(related_name='new_categoriess', verbose_name='new item category', to='base.ItemCategory'),
        ),
        migrations.AlterField(
            model_name='fixcategorymerge',
            name='old_category',
            field=models.ForeignKey(related_name='old_categoriess', verbose_name='old item category', to='base.ItemCategory', null=True),
        ),
    ]
