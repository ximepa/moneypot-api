# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0049_auto_20151001_1059'),
    ]

    operations = [
        migrations.AddField(
            model_name='place',
            name='has_chunks',
            field=models.BooleanField(default=False, verbose_name='has cells'),
        ),
    ]
