# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0059_auto_20151012_1138'),
    ]

    operations = [
        migrations.CreateModel(
            name='Transmutation',
            fields=[
                ('transaction_ptr', models.OneToOneField(primary_key=True, auto_created=True, serialize=False, to='base.Transaction', parent_link=True)),
            ],
            options={
                'verbose_name': 'Fix: transmutation',
                'verbose_name_plural': 'Fix: transmutations',
            },
            bases=('base.transaction',),
        ),
        migrations.CreateModel(
            name='TransmutationItem',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('quantity', models.DecimalField(decimal_places=3, verbose_name='quantity', max_digits=9)),
                ('cell', models.CharField(max_length=16, blank=True, null=True)),
                ('category', models.ForeignKey(verbose_name='item category', to='base.ItemCategory')),
                ('chunk', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, null=True, blank=True, to='base.ItemChunk')),
                ('serial', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, null=True, blank=True, to='base.ItemSerial')),
                ('transmutation', models.ForeignKey(verbose_name='transmutation', related_name='transmutation_items', to='base.Transmutation')),
                ('transmuted', models.ForeignKey(verbose_name='transmuted item category', related_name='transmuted_categories', to='base.ItemCategory')),
            ],
            options={
                'verbose_name': 'transmutation item',
                'verbose_name_plural': 'transmutation items',
            },
        ),
    ]
