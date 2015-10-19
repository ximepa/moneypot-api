# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0063_run_fix_chunks'),
    ]

    operations = [
        migrations.CreateModel(
            name='item_chunks_filtered',
            fields=[
            ],
            options={
                'proxy': True,
                'verbose_name': 'item_chunks_filtered',
            },
            bases=('base.itemchunk',),
        ),
    ]
