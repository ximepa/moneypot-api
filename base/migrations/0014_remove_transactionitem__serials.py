# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0013_auto_20150512_1751'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transactionitem',
            name='_serials',
        ),
    ]
