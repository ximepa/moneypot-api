# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0021_base_v_item_movement'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            CREATE OR REPLACE VIEW base_v_serial_movement(
                source_name,
                destination_name,
                item_category_name,
                quantity,
                destination_id,
                source_id,
                category_id,
                transaction_id,
                serial,
                serial_id,
                created_at,
                completed_at)
            AS
                SELECT base_place1.name AS source_name,
                    base_place.name AS destination_name,
                    base_itemcategory.name AS item_category_name,
                    base_transactionitem.quantity,
                    base_transactionitem.destination_id,
                    base_transaction.source_id,
                    base_transactionitem.category_id,
                    base_transactionitem.transaction_id,
                    base_itemserial.serial,
                    base_transactionitem.serial_id,
                    base_transaction.created_at,
                    base_transaction.completed_at
                FROM base_transaction
                    JOIN base_transactionitem ON base_transaction.id =
                        base_transactionitem.transaction_id
                    JOIN base_place ON base_transactionitem.destination_id = base_place.id
                    JOIN base_place base_place1 ON base_transaction.source_id =
                        base_place1.id
                    JOIN base_itemcategory ON base_transactionitem.category_id =
                        base_itemcategory.id
                    JOIN base_itemserial ON base_transactionitem.serial_id =
                        base_itemserial.id;
            """,
            reverse_sql="""
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
                    base_transaction.completed_at
                FROM base_transaction
                    JOIN base_transactionitem ON base_transaction.id = base_transactionitem.transaction_id
                    JOIN base_place ON base_transaction.destination_id = base_place.id
                    JOIN base_place base_place1 ON base_transaction.source_id = base_place1.id
                    JOIN base_itemcategory ON base_transactionitem.category_id = base_itemcategory.id
                    JOIN base_itemserial ON base_transactionitem.serial_id = base_itemserial.id;
            """
        )
    ]
