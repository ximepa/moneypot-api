# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0035_auto_20150928_1752'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cell',
            name='place',
            field=models.ForeignKey(related_name='cells', verbose_name='place', to='base.Place'),
        ),
        migrations.AlterField(
            model_name='cellitem',
            name='place',
            field=models.ForeignKey(related_name='cell_items', verbose_name='place', to='base.Place'),
        ),
    ]
