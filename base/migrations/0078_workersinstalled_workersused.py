# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0077_workersitem_workersreturn'),
    ]

    operations = [
        migrations.CreateModel(
            name='WorkersInstalled',
            fields=[
            ],
            options={
                'verbose_name': "worker's installed item",
                'proxy': True,
                'verbose_name_plural': "worker's installed items",
            },
            bases=('base.transaction',),
        ),
        migrations.CreateModel(
            name='WorkersUsed',
            fields=[
            ],
            options={
                'verbose_name': "worker's used item",
                'proxy': True,
                'verbose_name_plural': "worker's used items",
            },
            bases=('base.transaction',),
        ),
    ]
