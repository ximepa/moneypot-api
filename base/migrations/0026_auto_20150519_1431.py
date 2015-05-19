# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0025_auto_20150518_0925'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='quantity',
            field=models.DecimalField(default=0, verbose_name='quantity', max_digits=9, decimal_places=3),
        ),
    ]
