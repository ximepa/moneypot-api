# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def fill_cells(apps, schema_editor):
    CellItem = apps.get_model("base", "CellItem")
    for ci in CellItem.objects.all():
        ci.save()


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0041_place_has_cells'),
    ]

    operations = [
        migrations.RunPython(fill_cells, fill_cells),
    ]
