# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0051_transactionitem_chunk'),
    ]

    operations = [
        migrations.AlterField(
            model_name='place',
            name='has_chunks',
            field=models.BooleanField(default=False, verbose_name='has chunks'),
        ),
    ]
