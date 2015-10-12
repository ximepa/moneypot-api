# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import filebrowser.fields


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0058_geoname'),
    ]

    operations = [
        migrations.AlterField(
            model_name='itemcategory',
            name='photo',
            field=filebrowser.fields.FileBrowseField(null=True, verbose_name='Image', max_length=200, blank=True),
        ),
    ]
