# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0027_fixserialtransform'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fixserialtransform',
            name='new_serial',
            field=models.CharField(max_length=32, verbose_name='new serial'),
        ),
        migrations.AlterField(
            model_name='fixserialtransform',
            name='old_serial',
            field=models.CharField(max_length=32, verbose_name='old serial'),
        ),
    ]
