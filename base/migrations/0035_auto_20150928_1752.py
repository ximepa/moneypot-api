# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from base.models import PurchaseItem

def fill_cells(apps, schema_editor):
    # We can't import the Person model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    Cell = apps.get_model("base", "Cell")
    CellItem = apps.get_model("base", "CellItem")
    ItemSerial = apps.get_model("base", "ItemSerial")

    for pi in PurchaseItem.objects.filter(cell__isnull=False):
        category = pi.category
        place = pi.purchase.destination
        if not pi.cell:
            continue
        cell, created = Cell.objects.get_or_create(place_id=place.id, name=pi.cell)
        serials = pi.serials
        if len(serials):
            for serial in serials:
                try:
                    s = ItemSerial.objects.get(serial=serial)
                except ItemSerial.DoesNotExist:
                    pass
                else:
                    CellItem.objects.get_or_create(
                        place_id=place.id,
                        category_id=category.id,
                        serial_id=s.id,
                        cell_id=cell.id
                    )
        CellItem.objects.get_or_create(
            place_id=place.id,
            category_id=category.id,
            cell_id=cell.id,
            serial=None
        )


def fill_cells_reverse(apps, schema_editor):
    Cell = apps.get_model("base", "Cell")
    CellItem = apps.get_model("base", "CellItem")
    CellItem.objects.all().delete()
    Cell.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0034_auto_20150928_1752'),
    ]

    operations = [
        migrations.RunPython(fill_cells, fill_cells_reverse),
    ]
