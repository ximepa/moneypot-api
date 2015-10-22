# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0062_trigram_indexes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='geoname',
            name='name',
            field=models.CharField(unique=True, max_length=100),
        ),
    ]
