# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import filebrowser.fields


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0023_itemcategory_photo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='itemcategory',
            name='photo',
            field=filebrowser.fields.FileBrowseField(max_length=200, null=True, verbose_name=b'Image', blank=True),
        ),
    ]
