# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0061_transmutationitem_ti'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                CREATE EXTENSION pg_trgm;
                CREATE INDEX base_itemcategory_name_trgm_idx ON base_itemcategory USING gin (name gin_trgm_ops);
                CREATE INDEX base_place_name_trgm_idx ON base_place USING gin (name gin_trgm_ops);
                CREATE INDEX base_geoname_nameme_trgm_idx ON base_geoname USING gin (name gin_trgm_ops);
            """,
            reverse_sql="""
                DROP INDEX base_geoname_nameme_trgm_idx;
                DROP INDEX base_place_name_trgm_idx;
                DROP INDEX base_itemcategory_name_trgm_idx;
                DROP EXTENSION pg_trgm CASCADE;
            """
        )
    ]
