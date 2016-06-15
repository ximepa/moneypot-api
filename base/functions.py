# -*- encoding: utf-8 -*-
from django.db.models import Sum
from base.models import Item, Purchase, Transaction
from django.db.transaction import atomic, savepoint_rollback, savepoint, clean_savepoints
import time


class ChunkConsistencyError(RuntimeError):
    def __init__(self, message, errors):
        super(ChunkConsistencyError, self).__init__(message)
        self.errors = errors


def check_item_chunk_consistency(trans):
    items = Item.objects.filter(chunks__isnull=False).annotate(score = Sum('chunks__chunk'))
    for item in items:
        if not item.quantity == item.score:
            raise ChunkConsistencyError("%s: %s <> %s after %s" % (item, item.quantity, item.score, trans),
                                        [item, trans])


@atomic
def replay_purchases():
    Purchase.objects.update(is_completed=False, is_prepared=False)
    for purchase in Purchase.objects.all().order_by('completed_at'):
        print("\n\n====================================")
        print("------------------------------------")
        print("%s: %s" % (purchase.pk, purchase))
        for pi in purchase.purchase_items.all():
            print("   %s: %s" % (pi, pi.quantity))
        purchase.complete()
        check_item_chunk_consistency(purchase)
    # raise RuntimeError("all ok")


@atomic
def replay_transactions():
    Transaction.objects.update(is_completed=False, is_prepared=False)
    for transaction in Transaction.objects.all().order_by('completed_at'):
        print("\n\n====================================")
        print("------------------------------------")
        print("%s: %s" % (transaction.pk, transaction))
        for pi in transaction.transaction_items.all():
            print("   %s: %s" % (pi, pi.quantity))
        transaction.complete()
        check_item_chunk_consistency(transaction)
    # raise RuntimeError("all ok")


def replay_one(movement):
    print("%s: %s" % (movement.pk, movement))
    sid = savepoint()
    movement.complete()
    try:
        with atomic():
            check_item_chunk_consistency(movement)
    except ChunkConsistencyError as e:
        print(movement.source)
        print(movement.destination)
        item = e.errors[0]
        category = item.category
        source_item = movement.source.items.get(category=category)
        print(source_item.quantity)
        print(source_item.chunks.all())
        savepoint_rollback(sid)
        source_item = movement.source.items.get(category=category)
        print(source_item.quantity)
        print(source_item.chunks.all())
        raise RuntimeError(e)
    clean_savepoints()


@atomic
def replay():
    Purchase.objects.update(is_completed=False, is_prepared=False)
    Transaction.objects.update(is_completed=False, is_prepared=False)

    queue = {}
    i = 0

    for p in Purchase.objects.all().order_by('completed_at'):
        i += 1
        key = str(int(time.mktime(p.completed_at.timetuple()))) + str(i).zfill(8)
        if key in queue:
            raise RuntimeError(key)
        queue.update(
            {key: p}
        )

    for p in Transaction.objects.all().order_by('completed_at'):
        i += 1
        key = str(int(time.mktime(p.completed_at.timetuple()))) + str(i).zfill(8)
        if key in queue:
            raise RuntimeError(key)
        queue.update(
            {key: p}
        )

    for key in sorted(queue.keys()):
        print("\n\n====================================")
        print("------------------------------------")
        print(key)
        replay_one(queue[key])

    raise RuntimeError("all ok")
