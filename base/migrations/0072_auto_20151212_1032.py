# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.utils import timezone
from datetime import timedelta
border_time = timezone.now() - timedelta(days=1)


def noop(apps, schema_editor):
    pass


def fill_place_timestamps(apps, schema_editor):
    Transaction = apps.get_model("base", "Transaction")
    Place = apps.get_model("base", "Place")
    for p in Place.objects.filter(timestamp__gt=border_time):
        tt = Transaction.objects.filter(models.Q(source_id=p.pk)|models.Q(destination_id=p.pk)).order_by('created_at')
        if tt.count():
            p.timestamp = tt[0].created_at
        else:
            p.timestamp = timezone.now()
        p.save()


def fill_category_timestamps(apps, schema_editor):
    TransactionItem = apps.get_model("base", "TransactionItem")
    ItemCategory = apps.get_model("base", "ItemCategory")
    for p in ItemCategory.objects.filter(timestamp__gt=border_time):
        tt = TransactionItem.objects.filter(category_id=p.pk).order_by('transaction__created_at')
        if tt.count():
            p.timestamp = tt[0].transaction.created_at
        else:
            p.timestamp = timezone.now()
        p.save()


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('base', '0071_auto_20151212_1031'),
    ]

    operations = [
        migrations.RunPython(fill_place_timestamps, noop),
        migrations.RunPython(fill_category_timestamps, noop),
    ]