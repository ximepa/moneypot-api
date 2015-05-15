# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0018_auto_20150514_1735'),
    ]

    operations = [
        migrations.AddField(
            model_name='transactionitem',
            name='destination',
            field=models.ForeignKey(related_name='transaction_items', verbose_name='destination', blank=True, to='base.Place', null=True),
        ),
    ]
