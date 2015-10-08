# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0056_fixplacemerge_timestamp'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='fixplacemerge',
            options={'ordering': ['-timestamp'], 'verbose_name': 'fix: place merge', 'verbose_name_plural': 'fix: place merges'},
        ),
    ]
