# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0073_geonames_load_fixture'),
    ]

    operations = [
        migrations.CreateModel(
            name='Return',
            fields=[
                ('transaction_ptr', models.OneToOneField(auto_created=True, to='base.Transaction', parent_link=True, primary_key=True, serialize=False)),
            ],
            options={
                'verbose_name_plural': 'returns',
                'verbose_name': 'return',
            },
            bases=('base.transaction',),
        ),
        migrations.CreateModel(
            name='ReturnItem',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('quantity', models.DecimalField(verbose_name='quantity', decimal_places=3, max_digits=9)),
                ('cell', models.CharField(null=True, blank=True, max_length=16)),
                ('category', models.ForeignKey(verbose_name='item category', to='base.ItemCategory')),
                ('chunk', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='base.ItemChunk', null=True, blank=True)),
                ('ret', models.ForeignKey(related_name='return_items', to='base.Return', verbose_name='return')),
                ('serial', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='base.ItemSerial', null=True, blank=True)),
                ('source', models.ForeignKey(related_name='return_items', on_delete=django.db.models.deletion.SET_NULL, to='base.Place', null=True, blank=True, verbose_name='source')),
                ('ti', models.OneToOneField(related_name='return_item', to='base.TransactionItem', null=True, blank=True)),
            ],
            options={
                'verbose_name_plural': 'return items',
                'verbose_name': 'return item',
            },
        ),
    ]
