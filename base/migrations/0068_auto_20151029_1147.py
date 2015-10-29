# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0067_merge'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='purchaseitem',
            options={'permissions': (('view_item_price', 'view item price'),), 'verbose_name': 'purchase item', 'verbose_name_plural': 'purchase items'},
        ),
    ]
