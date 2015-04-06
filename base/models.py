# coding=utf-8
from decimal import Decimal

from django.db import models
from django.utils.translation import ugettext_lazy as _, ugettext
from mptt.models import MPTTModel, TreeForeignKey
from django.core.exceptions import ValidationError
from django.utils import timezone
import re


class Unit(models.Model):
    INTEGER = 0
    DECIMAL = 1
    UNIT_TYPES = (
        (INTEGER, _("integer unit")),
        (DECIMAL, _("decimal unit"))
    )

    name = models.CharField(_("name"), max_length=20, unique=True)
    unit_type = models.PositiveSmallIntegerField(_("unit type"), choices=UNIT_TYPES)

    class Meta:
        verbose_name = _("unit")
        verbose_name_plural = _("units")

    def __unicode__(self):
        return self.name


class ItemCategory(MPTTModel):
    name = models.CharField(_("name"), max_length=100, unique=True)
    unit = models.ForeignKey("Unit", verbose_name=_("unit"), blank=True, null=True)
    is_stackable = models.NullBooleanField(_("stackable"), blank=True, null=True)
    parent = TreeForeignKey('self', verbose_name=_("parent"), null=True, blank=True, related_name='children')

    class Meta:
        verbose_name = _("item category")
        verbose_name_plural = _("item categories")

    class MPTTMeta:
        order_insertion_by = ['name']

    def __unicode__(self):
        return self.name

    def clean_unit(self):
        obj = self
        while not obj.unit and obj.parent:
            obj = obj.parent
        if obj.unit:
            self.unit = obj.unit
        else:
            raise ValidationError({'unit': ugettext('Unit must be set for object or for one of its parents.')})

    def clean_is_stackable(self):
        obj = self
        while obj.is_stackable is None and obj.parent:
            obj = obj.parent
        if obj.is_stackable is not None:
            self.is_stackable = obj.is_stackable
        else:
            raise ValidationError(
                {'is_stackable': ugettext('Stackable must be set for object or for one of its parents.')})

    def clean(self):
        self.clean_unit()
        self.clean_is_stackable()

    def save(self, *args, **kwargs):
        self.full_clean()
        super(ItemCategory, self).save(*args, **kwargs)


class Place(MPTTModel):
    name = models.CharField(_("name"), max_length=100)
    parent = TreeForeignKey('self', verbose_name=_("parent"), null=True, blank=True, related_name='children')
    is_shop = models.BooleanField(_("is shop"), blank=True, default=False)

    class Meta:
        unique_together = (
            ('name', 'parent'),
        )
        permissions = (
            ('view_place', _('view place')),  # can view this
            ('view_items', _('view items')),  # can view items here
            ('view_items_quantity', _('view item quantity')),
            ('view_items_serial', _('view item serial')),
            ('accept_transactions', _('accept transactions')),  # for managers of place
            ('request_item_store', _('request item store')),  # for clients of place
            ('request_item_withdraw', _('request item withdraw')),  # for clients of place
            ('change_serial', _('change serial')),  # for super managers
            ('change_chunks', _('change chunks')),  # for super managers
            ('modify_items', _('modify items')),  # for shops only, create or delete items on remote shops
            ('make_purchase', _('make purchase')),  # make purchase of stored in shop items
            ('make_auto_purchase', _('make auto purchase')),  # make purchase from shop. Items don't need to be created
        )

    class MPTTMeta:
        order_insertion_by = ['name']

    def __unicode__(self):
        return self.name


class MovementItem(models.Model):
    category = models.ForeignKey("ItemCategory", verbose_name=_("item category"))
    quantity = models.DecimalField(_("quantity"), max_digits=9, decimal_places=3)
    _serials = models.TextField(blank=True, null=True)
    _chunks = models.TextField(blank=True, null=True)

    class Meta:
        abstract = True

    def clean_chunks(self):
        if not self._chunks:
            return

        chunks_str = re.findall(r"[\d\.]+", self._chunks)
        f = None
        if self.category.unit.unit_type == Unit.INTEGER:
            f = int
        if self.category.unit.unit_type == Unit.DECIMAL:
            f = Decimal
        if not f:
            raise ValidationError(ugettext("Category unit type is unknown"))
        try:
            chunks_data = map(f, chunks_str)
        except Exception, e:
            raise ValidationError({'_chunks': ugettext('data error: %s' % e)})
        total = reduce(lambda x, y: f(x + y), chunks_data, 0)
        if not total == self.quantity:
            raise ValidationError({
                '_chunks': ugettext(u'chunks sum error: {total}≠{quantity}'.format(
                    total=total,
                    quantity=self.quantity
                ))
            })
        self._chunks = ", ".join(map(str, chunks_data))
        return chunks_data

    @property
    def chunks(self):
        return self.clean_chunks()

    @chunks.setter
    def chunks(self, value):
        self._chunks = ", ".join(value)

    def clean_serials(self):
        if not self._serials:
            return

        if self.category.unit.unit_type == Unit.DECIMAL:
            raise ValidationError({'_serials': ugettext(
                'unit type `%s` can not have serials' % self.category.unit.name
            )})
        serials_data = re.findall(r"[\w-]+", self._serials)
        if not self.quantity == len(serials_data):
            raise ValidationError({'_serials': ugettext(
                u'serials count error: {count}≠{quantity}'.format(count=len(serials_data), quantity=self.quantity)
            )})
        self._serials = ", ".join(map(str, serials_data))
        return serials_data

    @property
    def serials(self):
        return self.clean_serials()

    @serials.setter
    def serials(self, value):
        self._serials = ", ".join(value)

    def clean_quantity(self):
        f = None
        if self.category.unit.unit_type == Unit.INTEGER:
            f = int
        if self.category.unit.unit_type == Unit.DECIMAL:
            f = Decimal

        if not f(self.quantity) == self.quantity:
            raise ValidationError({'quantity': ugettext(
                'unit type `%s` can not be decimal' % self.category.unit.name
            )})

    def clean(self):
        self.clean_quantity()
        self.clean_chunks()
        self.clean_serials()

    def save(self, *args, **kwargs):
        self.full_clean()
        super(MovementItem, self).save(*args, **kwargs)


class PurchaseItem(MovementItem):
    purchase = models.ForeignKey("Purchase", verbose_name=_("Purchase"), related_name="purchase_items")
    price = models.DecimalField(_("price"), max_digits=9, decimal_places=2)
    # Movement superclass
    # category = models.ForeignKey("ItemCategory", verbose_name=_("item category"))
    # quantity = models.DecimalField(_("quantity"), max_digits=9, decimal_places=3)
    # _serials = models.TextField(blank=True, null=True)
    # _chunks = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = _("purchase item")
        verbose_name_plural = _("purchase items")

    def __unicode__(self):
        return self.category.name


class Payer(models.Model):
    name = models.CharField(_("payer"), max_length=100)

    class Meta:
        verbose_name = _("payer")
        verbose_name_plural = _("payers")

    def __unicode__(self):
        return self.name


class Movement(models.Model):
    created_at = models.DateTimeField(_("created at"), default=timezone.now)
    completed_at = models.DateTimeField(_("completed at"), default=None, blank=True, null=True)

    is_prepared = False
    items_prepared = []

    class Meta:
        abstract = True

    def prepare_source(self):
        # TODO: source withdraw items
        pass

    def prepare_items(self):
        self.items_prepared = []
        self.is_prepared = False
        for purchase_item in self.purchase_items.all():
            purchase_item.item_set.all().delete()
            i = Item.objects.create(
                category=purchase_item.category, quantity=purchase_item.quantity, purchase=purchase_item)
            if purchase_item.chunks:
                for chunk in purchase_item.chunks:
                    ItemChunk.objects.create(item=i, chunk=chunk, purchase=purchase_item)
            if purchase_item.serials:
                for serial in purchase_item.serials:
                    ItemSerial.objects.create(item=i, serial=serial, purchase=purchase_item)
            self.items_prepared.append(i)
        self.is_prepared = True

    def check_auto_source(self):
        if hasattr(self, 'is_auto_source'):
            return self.is_auto_source
        return False

    def prepare(self):
        if not self.check_auto_source():
            self.prepare_source()
        self.prepare_items()


class Purchase(Movement):
    items = models.ManyToManyField("ItemCategory", through="PurchaseItem", verbose_name=_("items"))
    source = TreeForeignKey("Place", verbose_name=_("source"), related_name="purchase_sources")
    destination = TreeForeignKey("Place", verbose_name=_("destination"), related_name="purchase_destinations")
    is_auto_source = models.BooleanField(_("auto source"), blank=True, default=False)
    payer = models.ForeignKey("Payer", verbose_name=_("payer"))

    # Movement superclass
    # created_at = models.DateTimeField(_("created at"), default=timezone.now)
    # completed_at = models.DateTimeField(_("completed at"), default=None, blank=True, null=True)


    class Meta:
        verbose_name = _("purchase")
        verbose_name_plural = _("purchases")

    def __unicode__(self):
        return u'%s → %s' % (self.source.name, self.destination.name)
        # return u'%s -> %s' % (self.source.name, self.destination.name)

    def clean_is_auto_source(self):
        if self.is_auto_source and not self.source.is_shop:
            raise ValidationError({'is_auto_source': ugettext('auto source is allowed for shops only')})

    def clean(self):
        self.clean_is_auto_source()

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Purchase, self).save(*args, **kwargs)

    def complete(self):
        pass


class Item(models.Model):
    category = TreeForeignKey("ItemCategory", verbose_name=_("item category"), related_name='items')
    quantity = models.DecimalField(_("quantity"), max_digits=9, decimal_places=3)
    is_reserved = models.BooleanField(_("is reserved"), blank=True, default=False)
    place = TreeForeignKey("Place", verbose_name=_("place"), blank=True, null=True, related_name='items')
    purchase = models.ForeignKey("PurchaseItem", verbose_name=_("purchase"), blank=True, null=True)

    class Meta:
        verbose_name = _("item")
        verbose_name_plural = _("items")

    def __unicode__(self):
        return self.category.name

    @property
    def unit(self):
        return self.category.unit

    @property
    def is_stackable(self):
        return self.category.is_stackable


class ItemSerial(models.Model):
    item = models.ForeignKey("Item", verbose_name=_("item"), related_name='serials')
    serial = models.CharField(_("serial"), max_length=32, unique=True)
    purchase = models.ForeignKey("PurchaseItem", verbose_name=_("purchase"), blank=True, null=True)

    class Meta:
        verbose_name = _("serial")
        verbose_name_plural = _("serials")

    def __unicode__(self):
        return self.serial


class ItemLabel(models.Model):
    item = models.ForeignKey("Item", verbose_name=_("item"), related_name='labels')
    label = models.CharField(_("label"), max_length=32, unique=True)
    purchase = models.ForeignKey("PurchaseItem", verbose_name=_("purchase"), blank=True, null=True)

    class Meta:
        verbose_name = _("label")
        verbose_name_plural = _("labels")

    def __unicode__(self):
        return self.serial


class ItemChunk(models.Model):
    item = models.ForeignKey("Item", verbose_name=_("item"), related_name='chunks')
    chunk = models.DecimalField(max_digits=9, decimal_places=3)
    purchase = models.ForeignKey("PurchaseItem", verbose_name=_("purchase"), blank=True, null=True)

    class Meta:
        verbose_name = _("chunk")
        verbose_name_plural = _("chunks")

    def __unicode__(self):
        return self.serial


class TransactionItem(MovementItem):
    transaction = models.ForeignKey("Transaction", verbose_name=_("item transaction"), related_name="transaction_items")
    purchase = models.ForeignKey("Purchase", verbose_name=_("Purchase"),
                                 blank=True, null=True, related_name="transaction_items")
    # Movement superclass
    # category = models.ForeignKey("ItemCategory", verbose_name=_("item category"))
    # quantity = models.DecimalField(_("quantity"), max_digits=9, decimal_places=3)
    # _serials = models.TextField(blank=True, null=True)
    # _chunks = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = _("transaction item")
        verbose_name_plural = _("transaction items")

    def __unicode__(self):
        return self.category.name


class Transaction(Movement):
    items = models.ManyToManyField("ItemCategory", through="TransactionItem", verbose_name=_("items"))
    source = TreeForeignKey("Place", verbose_name=_("source"), related_name="transaction_sources")
    destination = TreeForeignKey("Place", verbose_name=_("source"), related_name="transaction_destinations")
    is_negotiated_source = models.BooleanField(_("source negotiated"), blank=True, default=False)
    is_negotiated_destination = models.BooleanField(_("destination negotiated"), blank=True, default=False)
    is_confirmed_source = models.BooleanField(_("source confirmed"), blank=True, default=False)
    is_confirmed_destination = models.BooleanField(_("destination confirmed"), blank=True, default=False)
    is_completed = models.BooleanField(_("is complete"), blank=True, default=False)

    # Movement superclass
    # created_at = models.DateTimeField(_("created at"), default=timezone.now)
    # completed_at = models.DateTimeField(_("completed at"), default=None, blank=True, null=True)
