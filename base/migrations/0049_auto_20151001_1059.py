# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0048_auto_20150930_1549'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cellitem',
            name='category',
        ),
        migrations.RemoveField(
            model_name='cellitem',
            name='cell',
        ),
        migrations.RemoveField(
            model_name='cellitem',
            name='place',
        ),
        migrations.RemoveField(
            model_name='cellitem',
            name='serial',
        ),
        migrations.AddField(
            model_name='transactionitem',
            name='cell_from',
            field=models.CharField(max_length=16, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='transactionitem',
            name='cell',
            field=models.CharField(max_length=16, null=True, blank=True),
        ),
        migrations.DeleteModel(
            name='CellItem',
        ),
    ]
