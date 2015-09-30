# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0043_auto_20150930_1032'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cell',
            name='name',
            field=models.CharField(max_length=10),
        ),
        migrations.AlterUniqueTogether(
            name='cell',
            unique_together=set([('place', 'name')]),
        ),
    ]
