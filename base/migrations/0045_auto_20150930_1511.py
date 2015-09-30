# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def fill_cellitem_isnull(apps, schema_editor):
    # We can't import the Person model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    CellItem = apps.get_model("base", "CellItem")
    CellItem.objects.filter(cell__isnull=False).update(cell_isnull=False)
    CellItem.objects.filter(cell__isnull=True).update(cell_isnull=True)


def fill_cellitem_isnull_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0044_auto_20150930_1033'),
    ]

    operations = [
        migrations.RunPython(fill_cellitem_isnull, fill_cellitem_isnull_reverse)
    ]

