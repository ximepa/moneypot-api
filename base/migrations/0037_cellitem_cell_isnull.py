# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0036_auto_20150928_1813'),
    ]

    operations = [
        migrations.AddField(
            model_name='cellitem',
            name='cell_isnull',
            field=models.BooleanField(default=True),
        ),
    ]
