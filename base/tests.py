from django.test import TestCase
from django.forms import ValidationError

# Create your tests here.

#Third-party app imports
from model_mommy import mommy
from model_mommy.recipe import Recipe, foreign_key
from decimal import Decimal

from.models import Unit, ItemCategory, Item, ItemSerial, ItemChunk, IncompatibleUnitException, InvalidParameters


class ItemTestCase(TestCase):
    unit_pcs = None
    unit_litre = None
    unit_m = None
    cat_router = None
    cat_fuel = None
    cat_cable = None

    @classmethod
    def setUpClass(cls):
        cls.unit_pcs = mommy.make(Unit, name='pcs', unit_type=Unit.INTEGER)
        cls.unit_litre = mommy.make(Unit, name='litre', unit_type=Unit.DECIMAL)
        cls.unit_m = mommy.make(Unit, name='m', unit_type=Unit.DECIMAL)
        cls.cat_router = mommy.make(ItemCategory, unit=cls.unit_pcs, is_stackable=True)
        cls.cat_fuel = mommy.make(ItemCategory, unit=cls.unit_litre, is_stackable=True)
        cls.cat_cable = mommy.make(ItemCategory, unit=cls.unit_m, is_stackable=False)

    @classmethod
    def tearDownClass(cls):
        cls.unit_pcs.delete()
        cls.unit_litre.delete()
        cls.unit_m.delete()
        cls.cat_router.delete()
        cls.cat_fuel.delete()
        cls.cat_cable.delete()

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
        # new_i = Item.objects.get(pk=i.pk)
        new_i = i
        self.assertEqual(result.quantity, Decimal(4))
        self.assertEqual(new_i.quantity, Decimal(6))
        self.assertEqual(result.is_reserved, True)
        self.assertEqual(new_i.is_reserved, False)
        self.assertEqual(result.category, i.category)
        self.assertEqual(result.purchase, i.purchase)
        self.assertEqual(result.place, i.place)

    def test_05_withdraw_pcs_float_fail(self):
        i = mommy.make(Item, category=self.cat_router, quantity=10)
        self.assertRaises(IncompatibleUnitException, i.withdraw, quantity=4.5)

    def test_06_withdraw_serial(self):
        i = mommy.make(Item, category=self.cat_router, quantity=10)
        serials = mommy.make(ItemSerial, _quantity=10, item=i)
        result = i.withdraw(quantity=2, serials=ItemSerial.objects.filter(pk__in=[serials[0].pk, serials[3].pk]))
        # new_i = Item.objects.get(pk=i.pk)
        new_i = i
        self.assertEqual(result.quantity, Decimal(2))
        self.assertEqual(new_i.quantity, Decimal(8))
        self.assertEqual(result.is_reserved, True)
        self.assertEqual(new_i.is_reserved, False)
        self.assertEqual(result.category, i.category)
        self.assertEqual(result.purchase, i.purchase)
        self.assertEqual(result.place, i.place)
        self.assertEqual(i.serials.count(), 8)
        self.assertEqual(result.serials.count(), 2)

    def test_06_withdraw_serial_count_fail(self):
        i = mommy.make(Item, category=self.cat_router, quantity=10)
        serials = mommy.make(ItemSerial, _quantity=10, item=i)
        self.assertRaises(InvalidParameters, i.withdraw,
                          quantity=2, serials=ItemSerial.objects.filter(pk__in=[serials[0].pk]))

    def test_06_withdraw_any_when_serial_fail(self):
        i = mommy.make(Item, category=self.cat_router, quantity=10)
        serials = mommy.make(ItemSerial, _quantity=10, item=i)
        self.assertRaises(InvalidParameters, i.withdraw, quantity=2)

