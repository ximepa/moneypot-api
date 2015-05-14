# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0017_vitemmovement_vserialmovement'),
    ]

    operations = [
        migrations.CreateModel(
            name='item_movement_filtered',
            fields=[
            ],
            options={
                'verbose_name': 'item_movement_filtered',
                'proxy': True,
            },
            bases=('base.vitemmovement',),
        ),
        migrations.CreateModel(
            name='serial_movement_filtered',
            fields=[
            ],
            options={
                'verbose_name': 'serial_movement_filtered',
                'proxy': True,
            },
            bases=('base.vserialmovement',),
        ),
        migrations.AlterModelOptions(
            name='vitemmovement',
            options={'ordering': ['-created_at'], 'managed': False, 'verbose_name': 'item movement', 'verbose_name_plural': 'items movements'},
        ),
        migrations.AlterModelOptions(
            name='vserialmovement',
            options={'ordering': ['-created_at'], 'managed': False, 'verbose_name': 'serial movement', 'verbose_name_plural': 'serials movements'},
        ),
    ]
