# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('base', '0020_auto_20150515_1521'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                CREATE OR REPLACE VIEW base_v_item_movement(
                    item_category_name,
                    source_name,
                    destination_name,
                    quantity,
                    destination_id,
                    source_id,
                    transaction_item_id,
                    category_id,
                    transaction_id,
                    created_at,
                    completed_at)
                AS
                    SELECT base_itemcategory.name AS item_category_name,
                        base_place1.name AS source_name,
                        base_place.name AS destination_name,
                        sum(base_transactionitem.quantity) AS quantity,
                        base_transactionitem.destination_id,
                        base_transaction.source_id,
                        max(base_transactionitem.id) AS transaction_item_id,
                        base_transactionitem.category_id,
                        base_transactionitem.transaction_id,
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
                    GROUP BY base_place1.name,
                        base_place.name,
                        base_transactionitem.destination_id,
                        base_transaction.source_id,
                        base_transactionitem.category_id,
                        base_transactionitem.transaction_id,
                        base_transaction.created_at,
                        base_transaction.completed_at,
                        base_itemcategory.name;
            """,
            reverse_sql="""
                CREATE OR REPLACE VIEW base_v_item_movement AS
                SELECT base_itemcategory.name AS item_category_name,
                    base_place1.name AS source_name,
                    base_place.name AS destination_name,
                    sum(base_transactionitem.quantity) AS quantity,
                    base_transaction.destination_id,
                    base_transaction.source_id,
                    MAX(base_transactionitem.id) as transaction_item_id,
                    base_transactionitem.category_id,
                    base_transactionitem.transaction_id,
                    base_transaction.created_at,
                    base_transaction.completed_at
                FROM base_transaction
                    JOIN base_transactionitem ON base_transaction.id = base_transactionitem.transaction_id
                    JOIN base_place ON base_transaction.destination_id = base_place.id
                    JOIN base_place base_place1 ON base_transaction.source_id = base_place1.id
                    JOIN base_itemcategory ON base_transactionitem.category_id = base_itemcategory.id
                GROUP BY
                    base_place1.name, base_place.name, base_transaction.destination_id,
                    base_transaction.source_id, base_transactionitem.category_id, base_transactionitem.transaction_id,
                    base_transaction.created_at, base_transaction.completed_at, base_itemcategory.name;
            """
        )
    ]
