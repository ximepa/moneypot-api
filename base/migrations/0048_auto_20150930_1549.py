# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def fill_serial_cell(apps, schema_editor):
    # We can't import the Person model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    CellItem = apps.get_model("base", "CellItem")
    ItemSerial = apps.get_model("base", "ItemSerial")
    serials = ItemSerial.objects.filter(item__place__has_cells=True)
    for serial in serials:
        ci = CellItem.objects.filter(place=serial.item.place, serial=serial)
        if ci.count():
            serial.cell = ci[0].cell
            serial.save()


def fill_serial_cell_reverse(apps, schema_editor):
    ItemSerial = apps.get_model("base", "ItemSerial")
    ItemSerial.objects.all().update(cell=None)

class Migration(migrations.Migration):

    dependencies = [
        ('base', '0047_auto_20150930_1549'),
    ]

    operations = [
        migrations.RunPython(fill_serial_cell, fill_serial_cell_reverse)
    ]
