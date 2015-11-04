# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0069_auto_20151030_1122'),
    ]

    operations = [
        migrations.AddField(
            model_name='transactionitem',
            name='purchase_item',
            field=models.ForeignKey(to='base.PurchaseItem', blank=True, verbose_name='purchase', null=True),
        ),
    ]
