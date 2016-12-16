# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0075_auto_20160823_1633'),
    ]

    operations = [
        migrations.CreateModel(
            name='StorageToWorkerTransaction',
            fields=[
            ],
            options={
                'verbose_name_plural': 'withdraws from storage',
                'verbose_name': 'withdraw from storage',
                'proxy': True,
            },
            bases=('base.transaction',),
        ),
    ]
