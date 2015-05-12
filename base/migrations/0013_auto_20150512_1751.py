# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations, transaction
import re
from copy import deepcopy


def transaction_items_single_serial(apps, schema_editor):
    # We can't import the Person model directly as it may be a newer
    # version than this migration expects. We use the historical version.

    Transaction = apps.get_model("base", "Transaction")
    TransactionItem = apps.get_model("base", "TransactionItem")
    ItemSerial = apps.get_model("base", "ItemSerial")

    serials_data = re.compile(r"[\w-]+")

    for ti in TransactionItem.objects.all().exclude(_serials__isnull=True).exclude(_serials__exact=''):
        with transaction.atomic():
            for serial in serials_data.findall(ti._serials):
                try:
                    s = ItemSerial.objects.get(serial=serial)
                except ItemSerial.DoesNotExist:
                    raise RuntimeError("serial %s does not exist! %s %s" % (serial, ti.pk, ti.transaction.pk))
                else:
                    nti = deepcopy(ti)
                    nti.pk = None
                    nti.quantity = 1
                    nti._serials = ""
                    nti.serial_id = s.pk
                    nti.save()
            ti.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0012_transactionitem_serial'),
    ]

    operations = [
        migrations.RunPython(transaction_items_single_serial),
    ]
