# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0065_base_v_serial_movement_fix'),
    ]

    operations = [
        migrations.CreateModel(
            name='Warranty',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('date', models.DateField(verbose_name='warranty date')),
                ('comment', models.TextField(verbose_name='comment', null=True, blank=True)),
                ('serial', models.OneToOneField(verbose_name='serial', to='base.ItemSerial')),
            ],
            options={
                'verbose_name_plural': 'warranty dates',
                'verbose_name': 'warranty date',
            },
        ),
    ]
