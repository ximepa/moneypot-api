# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0031_auto_20150925_1901'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchaseitem',
            name='cell',
            field=models.CharField(max_length=16, null=True, blank=True),
        ),
    ]
