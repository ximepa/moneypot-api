# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0003_purchase_is_completed'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='reserved_by',
            field=models.ForeignKey(verbose_name='reserved by transaction', blank=True, to='base.TransactionItem', null=True),
        ),
        migrations.AddField(
            model_name='purchase',
            name='is_prepared',
            field=models.BooleanField(default=False, verbose_name='is complete'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='is_prepared',
            field=models.BooleanField(default=False, verbose_name='is complete'),
        ),
        migrations.AlterField(
            model_name='item',
            name='category',
            field=models.ForeignKey(related_name='items', verbose_name='item category', to='base.ItemCategory'),
        ),
        migrations.AlterField(
            model_name='item',
            name='place',
            field=models.ForeignKey(related_name='items', verbose_name='place', blank=True, to='base.Place', null=True),
        ),
        migrations.AlterField(
            model_name='itemcategory',
            name='parent',
            field=models.ForeignKey(related_name='children', verbose_name='parent', blank=True, to='base.ItemCategory', null=True),
        ),
        migrations.AlterField(
            model_name='place',
            name='name',
            field=models.CharField(unique=True, max_length=100, verbose_name='name'),
        ),
        migrations.AlterField(
            model_name='place',
            name='parent',
            field=models.ForeignKey(related_name='children', verbose_name='parent', blank=True, to='base.Place', null=True),
        ),
        migrations.AlterField(
            model_name='purchase',
            name='destination',
            field=models.ForeignKey(related_name='purchase_destinations', verbose_name='destination', to='base.Place'),
        ),
        migrations.AlterField(
            model_name='purchase',
            name='source',
            field=models.ForeignKey(related_name='purchase_sources', verbose_name='source', to='base.Place'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='destination',
            field=models.ForeignKey(related_name='transaction_destinations', verbose_name='destination', to='base.Place'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='source',
            field=models.ForeignKey(related_name='transaction_sources', verbose_name='source', to='base.Place'),
        ),
    ]
