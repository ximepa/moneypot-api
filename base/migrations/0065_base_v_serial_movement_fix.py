# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0064_item_chunks_filtered'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                CREATE OR REPLACE VIEW base_v_serial_movement AS
                SELECT base_place1.name AS source_name,
                    base_place.name AS destination_name,
                    base_itemcategory.name AS item_category_name,
                    base_transactionitem.quantity,
                    base_transaction.destination_id,
                    base_transaction.source_id,
                    base_transactionitem.category_id,
                    base_transactionitem.transaction_id,
                    base_itemserial.serial,
                    base_transactionitem.serial_id,
                    base_transaction.created_at,
                    base_transaction.completed_at,
                    base_transactionitem.id as transaction_item_id
                FROM base_transaction
                    JOIN base_transactionitem ON base_transaction.id = base_transactionitem.transaction_id
                    JOIN base_place ON base_transaction.destination_id = base_place.id
                    JOIN base_place base_place1 ON base_transaction.source_id = base_place1.id
                    JOIN base_itemcategory ON base_transactionitem.category_id = base_itemcategory.id
                    JOIN base_itemserial ON base_transactionitem.serial_id = base_itemserial.id;
            """,
            reverse_sql="""
                DROP VIEW base_v_serial_movement;
                CREATE VIEW base_v_serial_movement AS
                SELECT base_place1.name AS source_name,
                    base_place.name AS destination_name,
                    base_itemcategory.name AS item_category_name,
                    base_transactionitem.quantity,
                    base_transaction.destination_id,
                    base_transaction.source_id,
                    base_transactionitem.category_id,
                    base_transactionitem.transaction_id,
                    base_itemserial.serial,
                    base_transactionitem.serial_id,
                    base_transaction.created_at,
                    base_transaction.completed_at
                FROM base_transaction
                    JOIN base_transactionitem ON base_transaction.id = base_transactionitem.transaction_id
                    JOIN base_place ON base_transaction.destination_id = base_place.id
                    JOIN base_place base_place1 ON base_transaction.source_id = base_place1.id
                    JOIN base_itemcategory ON base_transactionitem.category_id = base_itemcategory.id
                    JOIN base_itemserial ON base_transactionitem.serial_id = base_itemserial.id;
            """,
        )
    ]
