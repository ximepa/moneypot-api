# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def fill_cells(apps, schema_editor):
    CellItem = apps.get_model("base", "CellItem")
    for ci in CellItem.objects.all():
        if ci.cell:
            ci.cell_isnull = False
        else:
            ci.cell_isnull = True
        ci.save()
        if not ci.cell_isnull:
            other = CellItem.objects.filter(
                place=ci.place,
                category=ci.category,
                serial=ci.serial,
                cell_isnull=True
            )
            other.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0041_place_has_cells'),
    ]

    operations = [
        migrations.RunPython(fill_cells, fill_cells),
    ]
