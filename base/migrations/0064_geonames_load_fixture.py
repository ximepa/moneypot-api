# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

from django.core.management import call_command


def loadfixture(apps, schema_editor):
    call_command('loaddata', 'geoname_initial.json')


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0063_auto_20151022_1706'),
    ]

    operations = [
         migrations.RunPython(loadfixture, loadfixture),
    ]
