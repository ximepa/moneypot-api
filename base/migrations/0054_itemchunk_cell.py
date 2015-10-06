# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0053_auto_20151006_1647'),
    ]

    operations = [
        migrations.AddField(
            model_name='itemchunk',
            name='cell',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='base.Cell', null=True),
        ),
    ]
