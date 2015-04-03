# coding=utf-8
from django.db import models
from django.utils.translation import ugettext_lazy as _, ugettext
from mptt.models import MPTTModel, TreeForeignKey
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal
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

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        verbose_name = _("item category")
        verbose_name_plural = _("item categories")

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
        if not obj.is_stackable is None:
            self.is_stackable = obj.is_stackable
        else:
            raise ValidationError({'is_stackable': ugettext('Stackable must be set for object or for one of its parents.')})
    
    def clean(self):
        self.clean_unit()
        self.clean_is_stackable()

    def save(self, *args, **kwargs):
        self.full_clean()
        super(self, ItemCategory).save(*args, **kwargs)


class Place(MPTTModel):
    name = models.CharField(_("name"), max_length=100)
    parent = TreeForeignKey('self', verbose_name=_("parent"), null=True, blank=True, related_name='children')
    is_shop = models.BooleanField(_("is shop"), blank=True, default=False)

    class Meta:
        unique_together = (
            ('name', 'parent'),
        )
        permissions = (
            ('view_place', _('view place')),                        # can view this
            ('view_items', _('view items')),                        # can view items here
            ('view_items_quantity', _('view item quantity')),
            ('view_items_serial', _('view item serial')),
            ('accept_transactions', _('accept transactions')),      # for managers of place
            ('request_item_store', _('request item store')),        # for clients of place
            ('request_item_withdraw', _('request item withdraw')),  # for clients of place
            ('change_serial', _('change serial')),                  # for super managers
            ('change_chunks', _('change chunks')),                  # for super managers
            ('modify_items', _('modify items')),                    # for shops only, create or delete items on remote shops
            ('make_purchase', _('make purchase')),                  # make purchase of stored in shop items
            ('make_auto_purchase', _('make auto purchase')),        # make purchase from shop. Items don't need to be created
        )

    def __unicode__(self):
        return self.name


class PurchaseItem(models.Model):
    category = models.ForeignKey("ItemCategory", verbose_name=_("item category"))
    purchase = models.ForeignKey("Purchase", verbose_name=_("Purchase"))
    quantity = models.DecimalField(_("quantity"), max_digits=9, decimal_places=3)
    price = models.DecimalField(_("price"), max_digits=9, decimal_places=3)
    serials = models.TextField()
    chunks = models.TextField()

    class Meta:
        verbose_name = _("purchase item")
        verbose_name_plural = _("purchase items")

    def __unicode__(self):
        return self.category.name

    def clean_chunks(self):
        if not self.chunks:
            return

        chunks_str = re.findall(r"[\d\.]+", self.chunks)
        f = None
        if self.category.unit.unit_type == Unit.INTEGER:
            f = int
        if self.category.unit.unit_type == Unit.DECIMAL:
            f = Decimal
        if not f:
            raise ValidationError(ugettext("Category unit type is unknown"))
        try:
            # chunks_data = ", ".join(map(str, map(f, chunks_str)))
            chunks_data = map(f, chunks_str)
        except Exception, e:
            raise ValidationError({'chunks': ugettext('data error: %s' % e)})
        total = reduce(lambda x, y: f(x+y), chunks_data, 0)
        if not total == self.quantity:
            raise ValidationError({'chunks': ugettext(u'chunks sum error: %s≠%s' % (total, self.quantity))})
        self.chunks = ", ".join(map(str, chunks_data))

    def clean_serials(self):
        if not self.serials:
            return

        if self.category.unit.unit_type == Unit.DECIMAL:
            raise ValidationError({'serials': ugettext('unit type `%s` can not have serials' % self.category.unit.name)})
        serials = re.findall(r"[\w-]+",  self.serials)
        if not self.quantity == len(serials):
            raise ValidationError({'serials': ugettext(u'serials count error: %s≠%s' % (len(serials), self.quantity))})
        self.serials = ", ".join(map(str, serials))

    def clean(self):
        self.clean_chunks()
        self.clean_serials()

    def save(self, *args, **kwargs):
        self.full_clean()
        super(self, PurchaseItem).save(*args, **kwargs)


class Purchase(models.Model):
    created_at = models.DateTimeField(_("created at"), default=timezone.now)
    completed_at = models.DateTimeField(_("completed at"), default=None, blank=True, null=True)
    items = models.ManyToManyField("Item", through="PurchaseItem", verbose_name=_("items"))
    source = TreeForeignKey("Place", verbose_name=_("source"))
    destination = TreeForeignKey("Place", verbose_name=_("source"))
    is_auto_source = models.BooleanField(_("auto source"), blank=True, default=False)

    class Meta:
        verbose_name = _("purchase")
        verbose_name_plural = _("purchases")

    def __unicode__(self):
        return u'%s → %s' % (self.source.name, self.destination.name)

    def clean_is_auto_source(self):
        if self.is_auto_source and not self.source.is_shop:
            raise ValidationError({'is_auto_source': ugettext('auto source is allowed for shops only')})

    def clean(self):
        self.clean_is_auto_source()

    def save(self, *args, **kwargs):
        self.full_clean()
        super(self, Purchase).save(*args, **kwargs)

    def complete(self):
        pass


class Item(models.Model):
    category = TreeForeignKey("ItemCategory", verbose_name=_("item category"), related_name='items')
    quantity = models.DecimalField(_("quantity"), max_digits=9, decimal_places=3)
    is_reserved = models.BooleanField(_("is reserved"), blank=True, default=False)
    place = TreeForeignKey("Place", verbose_name=_("place"), blank=True, related_name='items')
    purchase = models.ForeignKey("Purchase", verbose_name=_("purchase"), blank=True, null=True)

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
    item = models.ForeignKey("Item", verbose_name=_("item"))
    serial = models.CharField(_("serial"), unique=True)

    class Meta:
        verbose_name = _("serial")
        verbose_name_plural = _("serials")

    def __unicode__(self):
        return self.serial


class Transaction(models.Model):
    created_at = models.DateTimeField(_("created at"), default=timezone.now)
    completed_at = models.DateTimeField(_("completed at"), default=timezone.now)
    items = models.ManyToManyField("Item", through="PurchaseItem", verbose_name=_("items"))
    source = TreeForeignKey("Place", verbose_name=_("source"))
    destination = TreeForeignKey("Place", verbose_name=_("source"))
    is_auto_source = models.BooleanField(_("auto source"), blank=True, default=False)