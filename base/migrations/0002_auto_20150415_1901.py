# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='itemchunk',
            name='label',
            field=models.CharField(max_length=32, unique=True, null=True, verbose_name='label', blank=True),
        ),
    ]
