# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0038_auto_20150929_1319'),
    ]

    operations = [
        migrations.AddField(
            model_name='transactionitem',
            name='cell',
            field=models.ForeignKey(blank=True, to='base.Cell', null=True),
        ),
    ]
