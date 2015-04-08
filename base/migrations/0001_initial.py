# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import mptt.fields
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('quantity', models.DecimalField(verbose_name='quantity', max_digits=9, decimal_places=3)),
                ('is_reserved', models.BooleanField(default=False, verbose_name='is reserved')),
            ],
            options={
                'verbose_name': 'item',
                'verbose_name_plural': 'items',
            },
        ),
        migrations.CreateModel(
            name='ItemCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=100, verbose_name='name')),
                ('is_stackable', models.NullBooleanField(verbose_name='stackable')),
                ('lft', models.PositiveIntegerField(editable=False, db_index=True)),
                ('rght', models.PositiveIntegerField(editable=False, db_index=True)),
                ('tree_id', models.PositiveIntegerField(editable=False, db_index=True)),
                ('level', models.PositiveIntegerField(editable=False, db_index=True)),
                ('parent', mptt.fields.TreeForeignKey(related_name='children', verbose_name='parent', blank=True, to='base.ItemCategory', null=True)),
            ],
            options={
                'verbose_name': 'item category',
                'verbose_name_plural': 'item categories',
            },
        ),
        migrations.CreateModel(
            name='ItemChunk',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('chunk', models.DecimalField(max_digits=9, decimal_places=3)),
                ('label', models.CharField(unique=True, max_length=32, verbose_name='label')),
                ('item', models.ForeignKey(related_name='chunks', verbose_name='item', to='base.Item')),
            ],
            options={
                'verbose_name': 'chunk',
                'verbose_name_plural': 'chunks',
            },
        ),
        migrations.CreateModel(
            name='ItemSerial',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('serial', models.CharField(unique=True, max_length=32, verbose_name='serial')),
                ('item', models.ForeignKey(related_name='serials', verbose_name='item', to='base.Item')),
            ],
            options={
                'verbose_name': 'serial',
                'verbose_name_plural': 'serials',
            },
        ),
        migrations.CreateModel(
            name='Payer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name='payer')),
            ],
            options={
                'verbose_name': 'payer',
                'verbose_name_plural': 'payers',
            },
        ),
        migrations.CreateModel(
            name='Place',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name='name')),
                ('is_shop', models.BooleanField(default=False, verbose_name='is shop')),
                ('lft', models.PositiveIntegerField(editable=False, db_index=True)),
                ('rght', models.PositiveIntegerField(editable=False, db_index=True)),
                ('tree_id', models.PositiveIntegerField(editable=False, db_index=True)),
                ('level', models.PositiveIntegerField(editable=False, db_index=True)),
                ('parent', mptt.fields.TreeForeignKey(related_name='children', verbose_name='parent', blank=True, to='base.Place', null=True)),
            ],
            options={
                'permissions': (('view_place', 'view place'), ('view_items', 'view items'), ('view_items_quantity', 'view item quantity'), ('view_items_serial', 'view item serial'), ('accept_transactions', 'accept transactions'), ('request_item_store', 'request item store'), ('request_item_withdraw', 'request item withdraw'), ('change_serial', 'change serial'), ('change_chunks', 'change chunks'), ('modify_items', 'modify items'), ('make_purchase', 'make purchase'), ('make_auto_purchase', 'make auto purchase')),
            },
        ),
        migrations.CreateModel(
            name='Purchase',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='created at')),
                ('completed_at', models.DateTimeField(default=None, null=True, verbose_name='completed at', blank=True)),
                ('is_auto_source', models.BooleanField(default=False, verbose_name='auto source')),
                ('destination', mptt.fields.TreeForeignKey(related_name='purchase_destinations', verbose_name='destination', to='base.Place')),
            ],
            options={
                'verbose_name': 'purchase',
                'verbose_name_plural': 'purchases',
            },
        ),
        migrations.CreateModel(
            name='PurchaseItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('quantity', models.DecimalField(verbose_name='quantity', max_digits=9, decimal_places=3)),
                ('_serials', models.TextField(null=True, blank=True)),
                ('_chunks', models.TextField(null=True, blank=True)),
                ('price', models.DecimalField(verbose_name='price', max_digits=9, decimal_places=2)),
                ('category', models.ForeignKey(verbose_name='item category', to='base.ItemCategory')),
                ('purchase', models.ForeignKey(related_name='purchase_items', verbose_name='Purchase', to='base.Purchase')),
            ],
            options={
                'verbose_name': 'purchase item',
                'verbose_name_plural': 'purchase items',
            },
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='created at')),
                ('completed_at', models.DateTimeField(default=None, null=True, verbose_name='completed at', blank=True)),
                ('is_negotiated_source', models.BooleanField(default=False, verbose_name='source negotiated')),
                ('is_negotiated_destination', models.BooleanField(default=False, verbose_name='destination negotiated')),
                ('is_confirmed_source', models.BooleanField(default=False, verbose_name='source confirmed')),
                ('is_confirmed_destination', models.BooleanField(default=False, verbose_name='destination confirmed')),
                ('is_completed', models.BooleanField(default=False, verbose_name='is complete')),
                ('destination', mptt.fields.TreeForeignKey(related_name='transaction_destinations', verbose_name='source', to='base.Place')),
            ],
            options={
                'verbose_name': 'transaction',
                'verbose_name_plural': 'transaction',
            },
        ),
        migrations.CreateModel(
            name='TransactionItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('quantity', models.DecimalField(verbose_name='quantity', max_digits=9, decimal_places=3)),
                ('_serials', models.TextField(null=True, blank=True)),
                ('_chunks', models.TextField(null=True, blank=True)),
                ('category', models.ForeignKey(verbose_name='item category', to='base.ItemCategory')),
                ('purchase', models.ForeignKey(related_name='transaction_items', verbose_name='Purchase', blank=True, to='base.Purchase', null=True)),
                ('transaction', models.ForeignKey(related_name='transaction_items', verbose_name='item transaction', to='base.Transaction')),
            ],
            options={
                'verbose_name': 'transaction item',
                'verbose_name_plural': 'transaction items',
            },
        ),
        migrations.CreateModel(
            name='Unit',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=20, verbose_name='name')),
                ('unit_type', models.PositiveSmallIntegerField(verbose_name='unit type', choices=[(0, 'integer unit'), (1, 'decimal unit')])),
            ],
            options={
                'verbose_name': 'unit',
                'verbose_name_plural': 'units',
            },
        ),
        migrations.AddField(
            model_name='transaction',
            name='items',
            field=models.ManyToManyField(to='base.ItemCategory', verbose_name='items', through='base.TransactionItem'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='source',
            field=mptt.fields.TreeForeignKey(related_name='transaction_sources', verbose_name='source', to='base.Place'),
        ),
        migrations.AddField(
            model_name='purchase',
            name='items',
            field=models.ManyToManyField(to='base.ItemCategory', verbose_name='items', through='base.PurchaseItem'),
        ),
        migrations.AddField(
            model_name='purchase',
            name='payer',
            field=models.ForeignKey(verbose_name='payer', to='base.Payer'),
        ),
        migrations.AddField(
            model_name='purchase',
            name='source',
            field=mptt.fields.TreeForeignKey(related_name='purchase_sources', verbose_name='source', to='base.Place'),
        ),
        migrations.AddField(
            model_name='itemserial',
            name='purchase',
            field=models.ForeignKey(verbose_name='purchase', blank=True, to='base.PurchaseItem', null=True),
        ),
        migrations.AddField(
            model_name='itemchunk',
            name='purchase',
            field=models.ForeignKey(verbose_name='purchase', blank=True, to='base.PurchaseItem', null=True),
        ),
        migrations.AddField(
            model_name='itemcategory',
            name='unit',
            field=models.ForeignKey(verbose_name='unit', blank=True, to='base.Unit', null=True),
        ),
        migrations.AddField(
            model_name='item',
            name='category',
            field=mptt.fields.TreeForeignKey(related_name='items', verbose_name='item category', to='base.ItemCategory'),
        ),
        migrations.AddField(
            model_name='item',
            name='place',
            field=mptt.fields.TreeForeignKey(related_name='items', verbose_name='place', blank=True, to='base.Place', null=True),
        ),
        migrations.AddField(
            model_name='item',
            name='purchase',
            field=models.ForeignKey(verbose_name='purchase', blank=True, to='base.PurchaseItem', null=True),
        ),
        migrations.AlterUniqueTogether(
            name='place',
            unique_together=set([('name', 'parent')]),
        ),
    ]
