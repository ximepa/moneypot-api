# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0045_auto_20150930_1511'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='cell',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='base.Cell', null=True),
        ),
        migrations.AddField(
            model_name='itemserial',
            name='cell',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='base.Cell', null=True),
        ),
    ]
