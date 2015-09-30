# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0042_auto_20150929_1736'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cell',
            name='name',
            field=models.CharField(unique=True, max_length=10),
        ),
    ]
