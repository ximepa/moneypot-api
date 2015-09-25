# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0029_category_item_fixcategorymerge'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='fixcategorymerge',
            options={'ordering': ['-timestamp'], 'verbose_name': 'fix: category merge', 'verbose_name_plural': 'fix: category merges'},
        ),
    ]
