# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, transaction


def transaction_items_destinatio_set_default(apps, schema_editor):

    TransactionItem = apps.get_model("base", "TransactionItem")

    with transaction.atomic():
        for ti in TransactionItem.objects.all():
            if ti.destination is None:
                ti.destination = ti.transaction.destination
                ti.save()


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0019_transactionitem_destination'),
    ]

    operations = [
        migrations.RunPython(transaction_items_destinatio_set_default),
    ]
