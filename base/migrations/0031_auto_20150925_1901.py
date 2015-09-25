# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0030_auto_20150925_1859'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fixcategorymerge',
            name='new_category',
            field=models.ForeignKey(related_name='new_categoriess', on_delete=django.db.models.deletion.DO_NOTHING, verbose_name='new item category', to='base.ItemCategory'),
        ),
        migrations.AlterField(
            model_name='fixcategorymerge',
            name='old_category',
            field=models.ForeignKey(related_name='old_categoriess', on_delete=django.db.models.deletion.DO_NOTHING, verbose_name='old item category', to='base.ItemCategory', null=True),
        ),
    ]
