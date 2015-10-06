# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0052_auto_20151006_1633'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='purchaseitem',
            name='_chunks',
        ),
        migrations.RemoveField(
            model_name='transactionitem',
            name='_chunks',
        ),
        migrations.AlterField(
            model_name='transactionitem',
            name='chunk',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='base.ItemChunk', null=True),
        ),
        migrations.AlterField(
            model_name='transactionitem',
            name='destination',
            field=models.ForeignKey(related_name='transaction_items', on_delete=django.db.models.deletion.SET_NULL, verbose_name='destination', blank=True, to='base.Place', null=True),
        ),
        migrations.AlterField(
            model_name='transactionitem',
            name='serial',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='base.ItemSerial', null=True),
        ),
    ]
