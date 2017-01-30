# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0076_storagetoworkertransaction'),
    ]

    operations = [
        migrations.CreateModel(
            name='WorkersItem',
            fields=[
            ],
            options={
                'proxy': True,
                'verbose_name': "worker's item",
                'verbose_name_plural': "worker's items",
            },
            bases=('base.item',),
        ),
        migrations.CreateModel(
            name='WorkersReturn',
            fields=[
            ],
            options={
                'proxy': True,
                'verbose_name': "worker's return from address",
                'verbose_name_plural': "worker's returns from addresses",
            },
            bases=('base.return',),
        ),
    ]
