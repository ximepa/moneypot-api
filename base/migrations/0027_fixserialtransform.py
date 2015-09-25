# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0026_auto_20150519_1431'),
    ]

    operations = [
        migrations.CreateModel(
            name='FixSerialTransform',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('old_serial', models.CharField(max_length=32, verbose_name='serial')),
                ('new_serial', models.CharField(max_length=32, verbose_name='serial')),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, verbose_name='item category', blank=True, to='base.ItemCategory', null=True)),
            ],
            options={
                'ordering': ['-timestamp'],
                'verbose_name': 'fix: serial transform',
                'verbose_name_plural': 'fix: serial transforms',
            },
        ),
    ]
