# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def fix_chunks(apps, schema_editor):
    Item = apps.get_model("base", "Item")
    ItemChunk = apps.get_model("base", "ItemChunk")
    items = Item.objects.filter(category__is_stackable=False, place__has_cells=True, chunks=None)
    for item in items:
        ItemChunk.objects.create(item=item, chunk=item.quantity, purchase=item.purchase, cell=item.cell)


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0062_trigram_indexes'),
    ]

    operations = [
        migrations.RunPython(fix_chunks, fix_chunks)
    ]

