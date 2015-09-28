# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0033_auto_20150928_1736'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cellitem',
            name='serial',
            field=models.OneToOneField(null=True, blank=True, to='base.ItemSerial', verbose_name='item serial'),
        ),
    ]
