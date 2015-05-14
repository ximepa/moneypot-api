# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0016_base_v_serial_movement'),
    ]

    operations = [
        migrations.CreateModel(
            name='VItemMovement',
            fields=[
                ('item_category_name', models.CharField(max_length=100, verbose_name='item_category')),
                ('source_name', models.CharField(max_length=100, verbose_name='source')),
                ('destination_name', models.CharField(max_length=100, verbose_name='destination')),
                ('quantity', models.DecimalField(verbose_name='quantity', max_digits=9, decimal_places=3)),
                ('transaction_item', models.OneToOneField(primary_key=True, on_delete=django.db.models.deletion.DO_NOTHING, serialize=False, to='base.TransactionItem', verbose_name='transaction_item')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='created at')),
                ('completed_at', models.DateTimeField(default=None, null=True, verbose_name='completed at', blank=True)),
            ],
            options={
                'verbose_name': 'item movement',
                'db_table': 'base_v_item_movement',
                'managed': False,
                'verbose_name_plural': 'items movements',
            },
        ),
        migrations.CreateModel(
            name='VSerialMovement',
            fields=[
                ('item_category_name', models.CharField(max_length=100, verbose_name='item_category')),
                ('source_name', models.CharField(max_length=100, verbose_name='source')),
                ('destination_name', models.CharField(max_length=100, verbose_name='destination')),
                ('quantity', models.DecimalField(verbose_name='quantity', max_digits=9, decimal_places=3)),
                ('serial', models.CharField(max_length=32, verbose_name='serial')),
                ('serial_id', models.OneToOneField(primary_key=True, db_column=b'serial_id', serialize=False, to='base.ItemSerial', on_delete=django.db.models.deletion.DO_NOTHING, verbose_name='serial')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='created at')),
                ('completed_at', models.DateTimeField(default=None, null=True, verbose_name='completed at', blank=True)),
            ],
            options={
                'verbose_name': 'serial movement',
                'db_table': 'base_v_serial_movement',
                'managed': False,
                'verbose_name_plural': 'serialss movements',
            },
        ),
    ]
