# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0009_auto_20150430_0931'),
    ]

    operations = [
        migrations.AddField(
            model_name='itemcategory',
            name='comment',
            field=models.TextField(null=True, verbose_name='comment', blank=True),
        ),
        migrations.AddField(
            model_name='place',
            name='comment',
            field=models.TextField(null=True, verbose_name='comment', blank=True),
        ),
        migrations.AddField(
            model_name='purchase',
            name='comment',
            field=models.TextField(null=True, verbose_name='comment', blank=True),
        ),
    ]
