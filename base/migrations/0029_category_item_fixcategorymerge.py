# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0028_auto_20150925_1020'),
    ]

    operations = [
        migrations.CreateModel(
            name='FixCategoryMerge',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('old_category_sav_id', models.PositiveIntegerField(null=True, blank=True)),
                ('old_category_sav_name', models.CharField(max_length=100, null=True, blank=True)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('data', models.TextField(null=True, blank=True)),
                ('new_category', models.ForeignKey(related_name='new_categoriess', on_delete=django.db.models.deletion.DO_NOTHING, verbose_name='item category', to='base.ItemCategory')),
                ('old_category', models.ForeignKey(related_name='old_categoriess', on_delete=django.db.models.deletion.DO_NOTHING, verbose_name='item category', to='base.ItemCategory', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='category_item',
            fields=[
            ],
            options={
                'verbose_name': 'category_item',
                'proxy': True,
            },
            bases=('base.item',),
        ),
    ]
