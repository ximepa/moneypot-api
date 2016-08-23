# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0074_return_returnitem'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='returnitem',
            name='chunk',
        ),
        migrations.AlterField(
            model_name='returnitem',
            name='serial',
            field=models.CharField(blank=True, null=True, max_length=32),
        ),
    ]
