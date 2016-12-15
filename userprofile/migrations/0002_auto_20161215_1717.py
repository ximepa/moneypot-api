# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userprofile', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                  TRUNCATE TABLE userprofile_profile;
                  INSERT INTO userprofile_profile SELECT * FROM profile_profile;
                """,
            reverse_sql="TRUNCATE TABLE userprofile_profile;"
        )
    ]
