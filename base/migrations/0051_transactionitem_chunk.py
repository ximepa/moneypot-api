# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0050_place_has_chunks'),
    ]

    operations = [
        migrations.AddField(
            model_name='transactionitem',
            name='chunk',
            field=models.ForeignKey(blank=True, to='base.ItemChunk', null=True),
        ),
    ]
