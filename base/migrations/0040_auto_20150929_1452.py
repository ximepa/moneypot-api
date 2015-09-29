# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0039_transactionitem_cell'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transactionitem',
            name='cell',
            field=models.CharField(max_length=16, null=True, verbose_name='Cell', blank=True),
        ),
    ]
