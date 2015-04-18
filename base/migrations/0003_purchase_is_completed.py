# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0002_auto_20150415_1901'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchase',
            name='is_completed',
            field=models.BooleanField(default=False, verbose_name='is complete'),
        ),
    ]
