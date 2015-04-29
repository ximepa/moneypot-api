# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0007_auto_20150424_1622'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContractItemSerial',
            fields=[
            ],
            options={
                'verbose_name': 'contract serial',
                'proxy': True,
                'verbose_name_plural': 'contract serials',
            },
            bases=('base.itemserial',),
        ),
        migrations.CreateModel(
            name='OrderItemSerial',
            fields=[
            ],
            options={
                'verbose_name': 'order serial',
                'proxy': True,
                'verbose_name_plural': 'order serials',
            },
            bases=('base.itemserial',),
        ),
        migrations.AlterModelOptions(
            name='item_serials_filtered',
            options={'verbose_name': 'item_serials_filtered'},
        ),
        migrations.AlterModelOptions(
            name='place_item',
            options={'verbose_name': 'place_item'},
        ),
    ]
