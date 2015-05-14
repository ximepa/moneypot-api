# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0016_base_v_serial_movement'),
    ]

    operations = [
        migrations.CreateModel(
            name='VItemMovement',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('item_category_name', models.CharField(max_length=100, verbose_name='item_category')),
                ('source_name', models.CharField(max_length=100, verbose_name='source')),
                ('destination_name', models.CharField(max_length=100, verbose_name='destination')),
                ('quantity', models.DecimalField(verbose_name='quantity', max_digits=9, decimal_places=3)),
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
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('item_category_name', models.CharField(max_length=100, verbose_name='item_category')),
                ('source_name', models.CharField(max_length=100, verbose_name='source')),
                ('destination_name', models.CharField(max_length=100, verbose_name='destination')),
                ('quantity', models.DecimalField(verbose_name='quantity', max_digits=9, decimal_places=3)),
                ('serial', models.CharField(max_length=32, verbose_name='serial')),
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
