# -*- encoding: utf-8 -*-
from __future__ import print_function, division, unicode_literals, absolute_import

from django.test import TransactionTestCase
from django.forms import ValidationError

# Create your tests here.

# Third-party app imports
from model_mommy import mommy
from decimal import Decimal

from .models import Unit, ItemCategory, Item, ItemSerial, ItemChunk, IncompatibleUnitException, InvalidParameters, \
    DryRun, Place, Purchase, PurchaseItem

from django.db import models


class ItemTestCase(TransactionTestCase):
    unit_pcs = None
    unit_litre = None
    unit_m = None
    cat_router = None
    cat_fuel = None
    cat_cable = None

    # @classmethod
    # def setUpClass(cls):
    #     cls.unit_pcs = mommy.make(Unit, name='pcs', unit_type=Unit.INTEGER)
    #     cls.unit_litre = mommy.make(Unit, name='litre', unit_type=Unit.DECIMAL)
    #     cls.unit_m = mommy.make(Unit, name='m', unit_type=Unit.DECIMAL)
    #     cls.cat_router = mommy.make(ItemCategory, unit=cls.unit_pcs, is_stackable=True)
    #     cls.cat_fuel = mommy.make(ItemCategory, unit=cls.unit_litre, is_stackable=True)
    #     cls.cat_cable = mommy.make(ItemCategory, unit=cls.unit_m, is_stackable=False)
    #
    # @classmethod
    # def tearDownClass(cls):
    #     cls.unit_pcs.delete()
    #     cls.unit_litre.delete()
    #     cls.unit_m.delete()
    #     cls.cat_router.delete()
    #     cls.cat_fuel.delete()
    #     cls.cat_cable.delete()

    def setUp(self):
        self.unit_pcs = mommy.make(Unit, name='pcs', unit_type=Unit.INTEGER)
        self.unit_litre = mommy.make(Unit, name='litre', unit_type=Unit.DECIMAL)
        self.unit_m = mommy.make(Unit, name='m', unit_type=Unit.DECIMAL)
        self.cat_router = mommy.make(ItemCategory, unit=self.unit_pcs, is_stackable=True)
        self.cat_fuel = mommy.make(ItemCategory, unit=self.unit_litre, is_stackable=True)
        self.cat_cable = mommy.make(ItemCategory, unit=self.unit_m, is_stackable=False)

    def tearDown(self):
        self.unit_pcs.delete()
        self.unit_litre.delete()
        self.unit_m.delete()
        self.cat_router.delete()
        self.cat_fuel.delete()
        self.cat_cable.delete()

    def test_00_item_create(self):
        i = mommy.make(Item, category=self.cat_router, quantity=10)
        self.assertEqual(i.unit, self.unit_pcs, "wrong item unit created")
        self.assertEqual(i.is_stackable, self.cat_router.is_stackable, "wrong item stacking ability")

    def test_01_item_create_decimal_pcs_fail(self):
        self.assertRaises(ValidationError, mommy.make, Item, category=self.cat_router, quantity=Decimal(10.5))
        self.assertRaises(ValidationError, mommy.make, Item, category=self.cat_router, quantity=10.5)

    def test_02_item_create_serials(self):
        i = mommy.make(Item, category=self.cat_router, quantity=10)
        serials = mommy.make(ItemSerial, _quantity=10, item=i)

    def test_03_item_create_chunks(self):
        i = mommy.make(Item, category=self.cat_router, quantity=10)
        chunks = mommy.make(ItemChunk, _quantity=4, item=i, chunk=Decimal(2.5))

    def test_04_withdraw_any(self):
        i = mommy.make(Item, category=self.cat_router, quantity=10)
        result = i.withdraw(quantity=4)
        self.assertEqual(result.quantity, Decimal(4))
        self.assertEqual(i.quantity, Decimal(6))
        self.assertEqual(result.is_reserved, True)
        self.assertEqual(i.is_reserved, False)
        self.assertEqual(result.category, i.category)
        self.assertEqual(result.purchase, i.purchase)
        self.assertEqual(result.place, i.place)

    def test_05_withdraw_pcs_float_fail(self):
        i = mommy.make(Item, category=self.cat_router, quantity=10)
        self.assertRaises(IncompatibleUnitException, i.withdraw, quantity=4.5)

    def test_06_withdraw_serial(self):
        i = mommy.make(Item, category=self.cat_router, quantity=10)
        serials = mommy.make(ItemSerial, _quantity=10, item=i)
        result = i.withdraw(quantity=1, serial=serials[0])
        self.assertEqual(result.quantity, Decimal(1))
        self.assertEqual(i.quantity, Decimal(9))
        self.assertEqual(result.is_reserved, True)
        self.assertEqual(i.is_reserved, False)
        self.assertEqual(result.category, i.category)
        self.assertEqual(result.purchase, i.purchase)
        self.assertEqual(result.place, i.place)
        self.assertEqual(i.serials.count(), 9)
        self.assertEqual(result.serials.count(), 1)

    def test_07_withdraw_serial_count_fail(self):
        i = mommy.make(Item, category=self.cat_router, quantity=10)
        serials = mommy.make(ItemSerial, _quantity=10, item=i)
        self.assertRaises(InvalidParameters, i.withdraw, quantity=2, serial=serials[0])

    def test_08_withdraw_any_when_serial_fail(self):
        i = mommy.make(Item, category=self.cat_router, quantity=10)
        serials = mommy.make(ItemSerial, _quantity=10, item=i)
        self.assertRaises(InvalidParameters, i.withdraw, quantity=2)

    def test_09_withdraw_atomic_test(self):
        self.assertEqual(Item.objects.count(), 0)
        i = mommy.make(Item, category=self.cat_router, quantity=10)
        self.assertEqual(Item.objects.count(), 1)
        self.assertEqual(i.quantity, 10)
        result = i.withdraw(quantity=2)
        self.assertEqual(Item.objects.count(), 2)
        self.assertEqual(i.quantity, 8)
        self.assertEqual(result.quantity, 2)
        self.assertRaises(DryRun, i.withdraw, quantity=2, dry_run=True)
        self.assertEqual(Item.objects.count(), 2)  # extra item not created due rollback
        self.assertEqual(i.quantity, 6)  # item not refreshed yet!
        i.refresh_from_db()
        self.assertEqual(i.quantity, 8)  # item reloaded

    def test_10_withdraw_all(self):
        self.assertEqual(Item.objects.count(), 0)
        i = mommy.make(Item, category=self.cat_router, quantity=10)
        self.assertEqual(Item.objects.count(), 1)
        self.assertEqual(i.quantity, 10)
        result = i.withdraw(quantity=10)
        # self.assertEqual(Item.objects.count(), 1) now it will be 2! zero quantities not clean!
        # self.assertRaises(Item.DoesNotExist, i.refresh_from_db)
        self.assertEqual(i.quantity, 0)
        self.assertEqual(result.quantity, 10)

    def test_11_deposit_withdrawed(self):
        i = mommy.make(Item, category=self.cat_router, quantity=10)
        result = i.withdraw(quantity=5)
        self.assertEqual(i.quantity, 5)
        i.deposit(result)
        self.assertEqual(i.quantity, 10)
        self.assertRaises(Item.DoesNotExist, result.refresh_from_db)

    def test_12_deposit_self_fail(self):
        i = mommy.make(Item, category=self.cat_router, quantity=10)
        self.assertRaises(InvalidParameters, i.deposit, i)

    def test_13_deposit_wrong_cat_fail(self):
        i = mommy.make(Item, category=self.cat_router, quantity=10)
        i2 = mommy.make(Item, category=self.cat_cable, quantity=10)
        self.assertRaises(InvalidParameters, i.deposit, i2)

    def test_14_deposit_same_cat(self):
        i = mommy.make(Item, category=self.cat_router, quantity=10)
        i2 = mommy.make(Item, category=self.cat_router, quantity=5)
        i.deposit(i2)
        self.assertEqual(i.quantity, 15)

    def test_15_deposit_not_saved_item_source_fail(self):
        i = mommy.make(Item, category=self.cat_router, quantity=10)
        i2 = mommy.prepare(Item, category=self.cat_router, quantity=5)
        self.assertRaises(InvalidParameters, i.deposit, i2)
        i2.save()
        i.deposit(i2)
        self.assertEqual(i.quantity, 15)

    def test_16_deposit_not_saved_item_source_fail(self):
        i = mommy.prepare(Item, category=self.cat_router, quantity=10)
        i2 = mommy.make(Item, category=self.cat_router, quantity=5)
        self.assertRaises(InvalidParameters, i.deposit, i2)
        i.save()
        i.deposit(i2)
        self.assertEqual(i.quantity, 15)

    def test_17_deposit_decimal_stackable(self):
        i = mommy.make(Item, category=self.cat_fuel, quantity=Decimal('11.4'))
        i2 = mommy.make(Item, category=self.cat_fuel, quantity=Decimal('2.25'))
        i.deposit(i2)
        self.assertEqual(i.is_stackable, True)
        self.assertEqual(i.quantity, Decimal('13.65'))
        self.assertEqual(ItemChunk.objects.count(), 0)

    def test_18_deposit_decimal_not_stackable(self):
        i = mommy.make(Item, category=self.cat_cable, quantity=Decimal('11.4'))
        i2 = mommy.make(Item, category=self.cat_cable, quantity=Decimal('2.25'))
        i.deposit(i2)
        self.assertEqual(i.is_stackable, False)
        self.assertEqual(i.quantity, Decimal('13.65'))
        self.assertEqual(ItemChunk.objects.count(), 2)
        for chunk in ItemChunk.objects.all():
            self.assertEqual(chunk.item, i)
        self.assertEqual(ItemChunk.objects.filter(item=i).aggregate(sum=models.Sum('chunk'))['sum'], i.quantity)


class MovementTestCase(TransactionTestCase):
    def setUp(self):
        self.unit_pcs = mommy.make(Unit, name='pcs', unit_type=Unit.INTEGER)
        self.unit_litre = mommy.make(Unit, name='litre', unit_type=Unit.DECIMAL)
        self.unit_m = mommy.make(Unit, name='m', unit_type=Unit.DECIMAL)
        self.cat_router = mommy.make(ItemCategory, unit=self.unit_pcs, is_stackable=True)
        self.cat_fuel = mommy.make(ItemCategory, unit=self.unit_litre, is_stackable=True)
        self.cat_cable = mommy.make(ItemCategory, unit=self.unit_m, is_stackable=False)
        self.source = mommy.make(Place, is_shop=False)
        self.destination = mommy.make(Place, is_shop=False)
        self.shop = mommy.make(Place, is_shop=True)

    def tearDown(self):
        self.unit_pcs.delete()
        self.unit_litre.delete()
        self.unit_m.delete()
        self.cat_router.delete()
        self.cat_fuel.delete()
        self.cat_cable.delete()

    def test_01_purchase_auto(self):
        p = mommy.make(Purchase, source=self.shop, destination=self.destination, is_auto_source=True)
        mommy.make(PurchaseItem, purchase=p, price=Decimal('13.52'), category=self.cat_router, quantity=10)
        mommy.make(PurchaseItem, purchase=p, price=Decimal('3.5'), category=self.cat_cable, quantity=Decimal('4.5'))
        p.prepare()
        self.assertEqual(p.is_prepared, True)
        self.assertEqual(p.items_prepared, list(self.shop.items.filter(purchase__purchase=p)))
        self.assertEqual([], list(self.destination.items.filter(purchase__purchase=p)))
        p.complete()
        self.assertEqual(p.items_prepared, list(self.destination.items.filter(purchase__purchase=p)))
        self.assertEqual([], list(self.shop.items.filter(purchase__purchase=p)))
