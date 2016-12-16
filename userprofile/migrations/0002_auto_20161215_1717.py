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
                  CREATE TABLE IF NOT EXISTS profile_profile (
                        id integer NOT NULL,
                        place_id integer,
                        user_id integer NOT NULL
                    );
                  INSERT INTO userprofile_profile SELECT * FROM profile_profile;
                """,
            reverse_sql="TRUNCATE TABLE userprofile_profile;"
        )
    ]
