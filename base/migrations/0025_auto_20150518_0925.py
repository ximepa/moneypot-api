# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.db import transaction

def transaction_items_destinatio_set_default(apps, schema_editor):

    TransactionItem = apps.get_model("base", "TransactionItem")

    with transaction.atomic():
        for ti in TransactionItem.objects.filter(destination__isnull=True):
            ti.destination = ti.transaction.destination
            ti.save()


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0024_auto_20150515_1757'),
    ]

    operations = [
        migrations.RunPython(transaction_items_destinatio_set_default),
    ]
