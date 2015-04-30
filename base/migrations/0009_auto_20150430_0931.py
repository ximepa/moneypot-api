# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0008_auto_20150429_1714'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchaseitem',
            name='price_usd',
            field=models.DecimalField(null=True, verbose_name='price usd', max_digits=9, decimal_places=2, blank=True),
        ),
        migrations.AddField(
            model_name='transaction',
            name='comment',
            field=models.TextField(null=True, verbose_name='comment', blank=True),
        ),
        migrations.AddField(
            model_name='transaction',
            name='comment_places',
            field=models.ManyToManyField(to='base.Place', verbose_name='comment places'),
        ),
    ]
