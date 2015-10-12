# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0060_transmutation_transmutationitem'),
    ]

    operations = [
        migrations.AddField(
            model_name='transmutationitem',
            name='ti',
            field=models.OneToOneField(to='base.TransactionItem', blank=True, null=True, related_name='transmutation_item'),
        ),
    ]
