# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0004_auto_20150418_1317'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='parent',
            field=models.ForeignKey(related_name='children', verbose_name='parent', blank=True, to='base.Item', null=True),
        ),
    ]
