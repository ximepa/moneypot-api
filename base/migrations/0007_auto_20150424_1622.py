# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0006_auto_20150424_1621'),
    ]

    operations = [
        migrations.AlterField(
            model_name='itemcategorycomment',
            name='comment',
            field=models.CharField(max_length=100, null=True, verbose_name='comment', blank=True),
        ),
        migrations.AlterField(
            model_name='itemcategorycomment',
            name='serial_last_code',
            field=models.CharField(max_length=12, null=True, verbose_name='last code', blank=True),
        ),
    ]
