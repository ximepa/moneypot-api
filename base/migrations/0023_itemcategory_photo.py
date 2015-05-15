# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0022_base_v_serial_movement'),
    ]

    operations = [
        migrations.AddField(
            model_name='itemcategory',
            name='photo',
            field=models.ImageField(upload_to=b'item_categories', null=True, verbose_name='photo', blank=True),
        ),
    ]
