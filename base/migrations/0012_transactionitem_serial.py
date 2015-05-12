# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0011_auto_20150430_1536'),
    ]

    operations = [
        migrations.AddField(
            model_name='transactionitem',
            name='serial',
            field=models.ForeignKey(blank=True, to='base.ItemSerial', null=True),
        ),
    ]
