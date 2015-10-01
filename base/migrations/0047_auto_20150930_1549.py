# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def fill_item_cell(apps, schema_editor):
    # We can't import the Person model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    CellItem = apps.get_model("base", "CellItem")
    Item = apps.get_model("base", "Item")
    items = Item.objects.filter(place__has_cells=True)
    for item in items:
        ci = CellItem.objects.filter(place=item.place, category=item.category)
        if ci.count():
            item.cell = ci[0].cell
            item.save()


def fill_item_cell_reverse(apps, schema_editor):
    Item = apps.get_model("base", "Item")
    Item.objects.all().update(cell=None)

class Migration(migrations.Migration):

    dependencies = [
        ('base', '0046_auto_20150930_1545'),
    ]

    operations = [
        migrations.RunPython(fill_item_cell, fill_item_cell_reverse)
    ]
