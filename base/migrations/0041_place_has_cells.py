# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0040_auto_20150929_1452'),
    ]

    operations = [
        migrations.AddField(
            model_name='place',
            name='has_cells',
            field=models.BooleanField(default=False, verbose_name='has cells'),
        ),
    ]
