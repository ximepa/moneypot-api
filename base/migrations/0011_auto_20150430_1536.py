# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0010_auto_20150430_0939'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='comment',
            field=models.TextField(null=True, verbose_name='comment', blank=True),
        ),
        migrations.AddField(
            model_name='itemchunk',
            name='comment',
            field=models.TextField(null=True, verbose_name='comment', blank=True),
        ),
        migrations.AddField(
            model_name='itemserial',
            name='comment',
            field=models.TextField(null=True, verbose_name='comment', blank=True),
        ),
    ]
