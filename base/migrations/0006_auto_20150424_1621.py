# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0005_item_parent'),
    ]

    operations = [
        migrations.CreateModel(
            name='ItemCategoryComment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('serial_prefix', models.CharField(unique=True, max_length=12, verbose_name='prefix')),
                ('serial_last_code', models.CharField(max_length=12, verbose_name='last code')),
                ('comment', models.CharField(max_length=100, verbose_name='comment', blank=True)),
                ('category', models.ForeignKey(related_name='comments', verbose_name='item category', to='base.ItemCategory')),
            ],
            options={
                'verbose_name': 'item category comment',
                'verbose_name_plural': 'item category comments',
            },
        ),
        migrations.CreateModel(
            name='item_serials_filtered',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('base.itemserial',),
        ),
        migrations.CreateModel(
            name='place_item',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('base.item',),
        ),
        migrations.AlterModelOptions(
            name='place',
            options={'verbose_name': 'place', 'verbose_name_plural': 'places', 'permissions': (('view_place', 'view place'), ('view_items', 'view items'), ('view_items_quantity', 'view item quantity'), ('view_items_serial', 'view item serial'), ('accept_transactions', 'accept transactions'), ('request_item_store', 'request item store'), ('request_item_withdraw', 'request item withdraw'), ('change_serial', 'change serial'), ('change_chunks', 'change chunks'), ('modify_items', 'modify items'), ('make_purchase', 'make purchase'), ('make_auto_purchase', 'make auto purchase'))},
        ),
        migrations.AlterField(
            model_name='purchase',
            name='is_completed',
            field=models.BooleanField(default=False, verbose_name='is completed'),
        ),
        migrations.AlterField(
            model_name='purchase',
            name='is_prepared',
            field=models.BooleanField(default=False, verbose_name='is prepared'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='is_completed',
            field=models.BooleanField(default=False, verbose_name='is completed'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='is_prepared',
            field=models.BooleanField(default=False, verbose_name='is prepared'),
        ),
    ]
