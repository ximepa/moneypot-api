# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0068_auto_20151029_1147'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cell',
            name='name',
            field=models.CharField(max_length=32),
        ),
    ]
