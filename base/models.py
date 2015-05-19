# coding=utf-8
from decimal import Decimal

from django.db import models, IntegrityError
from django.utils.translation import ugettext_lazy as _, ugettext
from mptt.models import MPTTModel
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import transaction
from filebrowser.fields import FileBrowseField
import re


class IncompatibleUnitException(ValueError):
    pass


class ItemNotFound(ValueError):
    pass


class QuantityNotEnough(ValueError):
    pass


class InvalidParameters(ValueError):
    pass


class DryRun(RuntimeError):
    pass


class TransactionNotReady(RuntimeError):
    pass


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
    parent = models.ForeignKey('self', verbose_name=_("parent"), null=True, blank=True, related_name='children')
    comment = models.TextField(_("comment"), blank=True, null=True)
    photo = FileBrowseField("Image", max_length=200, directory="uploads", blank=True, null=True)

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


class ItemCategoryComment(models.Model):
    category = models.ForeignKey("ItemCategory", verbose_name=_("item category"), related_name="comments")
    serial_prefix = models.CharField(max_length=12, verbose_name=_("prefix"), unique=True)
    serial_last_code = models.CharField(max_length=12, verbose_name=_("last code"), blank=True, null=True)
    comment = models.CharField(max_length=100, verbose_name=_("comment"), blank=True, null=True)

    class Meta:
        verbose_name = _("item category comment")
        verbose_name_plural = _("item category comments")

    def __unicode__(self):
        return "%s - %s" % (self.category.name, self.serial_prefix)


class Place(MPTTModel):
    name = models.CharField(_("name"), max_length=100, unique=True)
    parent = models.ForeignKey('self', verbose_name=_("parent"), null=True, blank=True, related_name='children')
    is_shop = models.BooleanField(_("is shop"), blank=True, default=False)
    comment = models.TextField(_("comment"), blank=True, null=True)

    class Meta:
        verbose_name = _("place")
        verbose_name_plural = _("places")
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

    def get_absolute_url(self):
        return reverse('admin:base_place_item_changelist', args=[self.pk])

    def deposit(self, item):
        try:
            i = self.items.get(category=item.category, is_reserved=False)
        except Item.DoesNotExist:
            item.place = self
            item.is_reserved = False
            item.reserved_by = None
            item.parent = None
            item.save()
        else:
            i.deposit(item)

    def withdraw(self, item):
        try:
            i = self.items.get(category=item.category, is_reserved=False, quantity__gt=0)
        except Item.DoesNotExist:
            raise ItemNotFound(_("Can not withdraw <{item}> from <{place}>: not found.".format(
                item=item,
                place=self
            )))
        else:
            serial = None
            if item.serial:
                if not item.quantity == 1:
                    raise InvalidParameters(_("Can not withdraw <{item}> from <{place}>: quantity >1 for serial <{serial}> ".format(
                        item=item,
                        place=self,
                        serial=serial
                    )))
                try:
                    serial = i.serials.get(serial=item.serial)
                except ItemSerial.DoesNotExist:
                    raise ItemNotFound(_("Can not withdraw <{item}> from <{place}>: serial <{serial}> not found".format(
                        item=item,
                        place=self,
                        serial=serial
                    )))
            return i.withdraw(quantity=item.quantity, serial=serial)


class MovementItem(models.Model):
    category = models.ForeignKey("ItemCategory", verbose_name=_("item category"))
    quantity = models.DecimalField(_("quantity"), max_digits=9, decimal_places=3)
    _chunks = models.TextField(blank=True, null=True)

    class Meta:
        abstract = True

    def clean_chunks(self):
        if not self._chunks:
            return []

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

    def save(self, *args, **kwargs):
        self.full_clean()
        super(MovementItem, self).save(*args, **kwargs)


class PurchaseItem(MovementItem):
    purchase = models.ForeignKey("Purchase", verbose_name=_("Purchase"), related_name="purchase_items")
    price = models.DecimalField(_("price"), max_digits=9, decimal_places=2)
    price_usd = models.DecimalField(_("price usd"), max_digits=9, decimal_places=2, blank=True, null=True)
    # Movement superclass
    # category = models.ForeignKey("ItemCategory", verbose_name=_("item category"))
    # quantity = models.DecimalField(_("quantity"), max_digits=9, decimal_places=3)
    _serials = models.TextField(blank=True, null=True)
    # _chunks = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = _("purchase item")
        verbose_name_plural = _("purchase items")

    def __unicode__(self):
        return self.category.name

    def clean_serials(self):
        if not self._serials:
            return []

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

    def clean(self):
        self.clean_serials()

    def save(self, *args, **kwargs):
        self.full_clean()
        super(PurchaseItem, self).save(*args, **kwargs)


class Payer(models.Model):
    name = models.CharField(_("payer"), max_length=100)

    class Meta:
        verbose_name = _("payer")
        verbose_name_plural = _("payers")

    def __unicode__(self):
        return self.name


class Movement(models.Model):
    items_prepared = []
    created_at = models.DateTimeField(_("created at"), default=timezone.now)
    completed_at = models.DateTimeField(_("completed at"), default=None, blank=True, null=True)
    is_completed = models.BooleanField(_("is completed"), blank=True, default=False)
    is_prepared = models.BooleanField(_("is prepared"), blank=True, default=False)

    class Meta:
        abstract = True


class Purchase(Movement):
    items = models.ManyToManyField("ItemCategory", through="PurchaseItem", verbose_name=_("items"))
    source = models.ForeignKey("Place", verbose_name=_("source"), related_name="purchase_sources")
    destination = models.ForeignKey("Place", verbose_name=_("destination"), related_name="purchase_destinations")
    is_auto_source = models.BooleanField(_("auto source"), blank=True, default=False)
    payer = models.ForeignKey("Payer", verbose_name=_("payer"))
    comment = models.TextField(_("comment"), blank=True, null=True)

    # Movement superclass
    # created_at = models.DateTimeField(_("created at"), default=timezone.now)
    # completed_at = models.DateTimeField(_("completed at"), default=None, blank=True, null=True)
    # is_completed = models.BooleanField(_("is completed"), blank=True, default=False)
    # is_prepared = models.BooleanField(_("is prepared"), blank=True, default=False)

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

    def prepare_items_auto(self):
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
                purchase_item.serials.sort()
                for serial in purchase_item.serials:
                    try:
                        with transaction.atomic():
                            ItemSerial.objects.create(item=i, serial=serial, purchase=purchase_item)
                    except IntegrityError:
                        try:
                            item_serial = ItemSerial.objects.get(serial=serial)
                        except Item.DoesNotExist:
                            raise IntegrityError("serial %s duplicate but not found" % serial)
                        else:
                            raise IntegrityError("serial %s duplicate. item <%s> place <%s> pk <%s>" % (
                                serial,
                                item_serial.item.__unicode__(),
                                item_serial.item.place.__unicode__() if item_serial.item.place else None,
                                item_serial.item.pk
                            ))
            self.items_prepared.append(i)
        self.source.items.add(*self.items_prepared)
        self.is_prepared = True
        self.save()

    @transaction.atomic
    def prepare(self):
        if self.is_auto_source:
            self.prepare_items_auto()

    @transaction.atomic
    def complete(self):
        if self.is_completed:
            return
        self.prepare()
        prepared = self.is_prepared
        t = Transaction.objects.create(source=self.source, destination=self.destination)
        for pi in self.purchase_items.all():

            if not pi.serials:
                ti = TransactionItem.objects.create(purchase=self, transaction=t, category=pi.category,
                                                    quantity=pi.quantity, serial=None,
                                                    _chunks=pi._chunks, destination=self.destination)  # noqa

                for item in pi.item_set.all():
                    item.is_reserved = True
                    item.reserved_by = ti
                    item.save()
            else:
                prepared = False

                for serial in pi.serials:
                    item = pi.item_set.get()
                    s, created = ItemSerial.objects.get_or_create(item=item, serial=serial)
                    s.purchase = pi
                    s.save()
                    ti = TransactionItem.objects.create(purchase=self, transaction=t, category=pi.category,
                                                        quantity=1, serial=s, _chunks=pi._chunks)  # noqa

        t.is_prepared = prepared
        t.is_negotiated_source = True
        t.is_negotiated_destination = True
        t.is_confirmed_source = True
        t.is_confirmed_destination = True
        t.complete()

        self.completed_at = timezone.now()
        self.is_completed = True
        self.save()


class Item(models.Model):
    category = models.ForeignKey("ItemCategory", verbose_name=_("item category"), related_name='items')
    quantity = models.DecimalField(_("quantity"), max_digits=9, decimal_places=3)
    is_reserved = models.BooleanField(_("is reserved"), blank=True, default=False)
    reserved_by = models.ForeignKey("TransactionItem", verbose_name=_("reserved by transaction"), blank=True, null=True)
    parent = models.ForeignKey('self', verbose_name=_("parent"), blank=True, null=True, related_name="children")
    place = models.ForeignKey("Place", verbose_name=_("place"), blank=True, null=True, related_name='items')
    purchase = models.ForeignKey("PurchaseItem", verbose_name=_("purchase"), blank=True, null=True)
    comment = models.TextField(_("comment"), blank=True, null=True)

    class Meta:
        verbose_name = _("item")
        verbose_name_plural = _("items")

    def __unicode__(self):
        return self.category.name

    def get_absolute_url(self):
        return reverse('admin:base_item_serials_filtered_changelist', args=[self.pk])

    @property
    def unit(self):
        return self.category.unit

    @property
    def is_stackable(self):
        return self.category.is_stackable

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

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Item, self).save(*args, **kwargs)

    @property
    def qs(self):
        return self.__class__.objects.filter(pk=self.pk)

    # noinspection DjangoOrm
    def withdraw_any(self, quantity):
        """
        :param quantity: Amount of items to withdraw
        :type quantity: int or Decimal
        :returns: Item created in result of withdrawal spit request.
                  Marked as reserved until transaction will be completed or cancelled
        :rtype: base.models.Item()
        """

        if self.quantity - self.serials.count() < quantity:
            raise InvalidParameters(_("please provide serial to withdraw"))
        if self.chunks.count() and self.quantity - self.chunks.aggregate(models.Sum('chunk'))['chunk__sum'] < quantity:
            raise InvalidParameters(_("please provide chunk to withdraw"))
        item = Item.objects.create(
            quantity=quantity,
            is_reserved=True,
            purchase=self.purchase,
            category=self.category,
            place=self.place,
            parent=self,
        )
        return item

    # noinspection DjangoOrm
    def withdraw_serial(self, quantity, serial):
        """
        :param quantity: Amount of items to withdraw
        :type quantity: int or Decimal
        :param serial: instance of base.models.ItemSerial
        :type serial: base.models.ItemSerial()
        :returns: Item created in result of withdrawal spit request.
                  Marked as reserved until transaction will be completed or cancelled
        :rtype: base.models.Item()
        """
        if not quantity == 1:
            raise InvalidParameters(_("Serials count does not match requested quantity"))
        if not serial.item == self:
            raise InvalidParameters(_("Serial {serial} doesn't belong to item {item}".format(
                serial=serial.serial,
                item=self.__unicode__()
            )))
        item = Item.objects.create(
            quantity=quantity,
            is_reserved=True,
            purchase=self.purchase,
            category=self.category,
            place=self.place,
            parent=self,
        )
        serial.item=item
        serial.save()
        return item

    def withdraw_chunk(self, quantity, chunks):
        """
        :param quantity: Amount of items to withdraw
        :type quantity: int or Decimal
        :param chunks: Queryset of base.models.ItemChunk
        :type chunks: django.db.models.Queryset()
        :returns: Item created in result of withdrawal spit request.
                  Marked as reserved until transaction will be completed or cancelled
        :rtype: base.models.Item()
        """
        for chunk in chunks:
            if not chunk.item == self:
                raise InvalidParameters(_("Chunk {chunk} doesn't belong to item {item}".format(
                    chunk=chunk.__unicode__(),
                    item=self.__unicode__()
                )))
        if not chunks.aggregate(models.Sum('chunk'))['chunk__sum'] == quantity:
            raise InvalidParameters(_("Chunks total sum does not match requested quantity"))
        item = Item.objects.create(
            quantity=quantity,
            is_reserved=True,
            purchase=self.purchase,
            category=self.category,
            place=self.place,
            parent=self,
        )
        chunks.update(item=item)
        return item

    @transaction.atomic
    def withdraw(self, quantity, serial=None, chunks=None, dry_run=False):
        """
        :param quantity: Amount of items to withdraw
        :type quantity: int or Decimal
        :param serial: optional, instance of base.models.ItemSerial
        :type serial: base.models.ItemSerial()
        :param chunks: optional, Queryset of base.models.ItemChunk
        :type chunks: django.db.models.Queryset()
        :returns: Item created in result of withdrawal spit request.
                  Marked as reserved until transaction will be completed or cancelled
        :rtype: base.models.Item()
        """

        if self.unit.unit_type == Unit.INTEGER:
            if not int(quantity) == quantity:
                raise IncompatibleUnitException(_("Unit {unit} can not have value {quantity}".format(
                    unit=self.unit.name,
                    quantity=quantity)
                ))
        if quantity > self.quantity:
            raise QuantityNotEnough(_("Requested quantity more than available"))

        if serial:
            item = self.withdraw_serial(quantity, serial)
        elif chunks:
            item = self.withdraw_chunk(quantity, chunks)
        else:
            item = self.withdraw_any(quantity)

        self.qs.update(quantity=models.F('quantity') - quantity)
        self.refresh_from_db()

        # if self.quantity == 0:
        # self.children.update(parent=None)
        # self.delete()

        if dry_run:
            raise DryRun(_("Cancelled due to dry_run option"))

        return item

    @transaction.atomic
    def deposit(self, item, dry_run=False):
        """
        :param item: item to join with current, categiry must match
        :type item: base.models.Item()
        :returns: updated item (self)
        :rtype: base.models.Item()
        """

        if not isinstance(item, Item):
            raise InvalidParameters(_("item parameter must be instance of base.models.Item"))

        if not self.category == item.category:
            raise InvalidParameters(_("Item category must match"))

        if not self.pk:
            raise InvalidParameters(_("Destination item must exist in db"))

        if not item.pk:
            raise InvalidParameters(_("Source item must exist in db"))

        if self.pk == item.pk:
            raise InvalidParameters(_("Can't join item with itself"))

        if not item.is_stackable:
            if not item.chunks.count():
                ItemChunk.objects.create(item=item, chunk=item.quantity, purchase=item.purchase)
            if not self.chunks.count():
                ItemChunk.objects.create(item=self, chunk=self.quantity, purchase=self.purchase)

        self.qs.update(quantity=models.F('quantity') + item.quantity)
        self.refresh_from_db()

        item.chunks.update(item=self)
        item.serials.update(item=self)

        item.delete()

        if dry_run:
            raise DryRun(_("Cancelled due to dry_run option"))

        return self


class ItemSerial(models.Model):
    item = models.ForeignKey("Item", verbose_name=_("item"), related_name='serials')
    serial = models.CharField(_("serial"), max_length=32, unique=True)
    purchase = models.ForeignKey("PurchaseItem", verbose_name=_("purchase"), blank=True, null=True)
    comment = models.TextField(_("comment"), blank=True, null=True)

    class Meta:
        verbose_name = _("serial")
        verbose_name_plural = _("serials")

    def __unicode__(self):
        return self.serial

    def category_name(self):
        return self.item.category.name


class ItemChunk(models.Model):
    item = models.ForeignKey("Item", verbose_name=_("item"), related_name='chunks')
    chunk = models.DecimalField(max_digits=9, decimal_places=3)
    label = models.CharField(_("label"), max_length=32, unique=True, blank=True, null=True)
    purchase = models.ForeignKey("PurchaseItem", verbose_name=_("purchase"), blank=True, null=True)
    comment = models.TextField(_("comment"), blank=True, null=True)

    class Meta:
        verbose_name = _("chunk")
        verbose_name_plural = _("chunks")

    def __unicode__(self):
        return "%s%s" % (self.chunk, (" %s" % self.label) if self.label else "")

    def category_name(self):
        return self.item.category.name


class TransactionItem(MovementItem):
    transaction = models.ForeignKey("Transaction", verbose_name=_("item transaction"), related_name="transaction_items")
    purchase = models.ForeignKey("Purchase", verbose_name=_("Purchase"),
                                 blank=True, null=True, related_name="transaction_items")
    # Movement superclass
    # category = models.ForeignKey("ItemCategory", verbose_name=_("item category"))
    # quantity = models.DecimalField(_("quantity"), max_digits=9, decimal_places=3)
    # _chunks = models.TextField(blank=True, null=True)
    serial = models.ForeignKey(ItemSerial, blank=True, null=True)
    destination = models.ForeignKey("Place", verbose_name=_("destination"),
                                    related_name="transaction_items", blank=True, null=True)

    class Meta:
        verbose_name = _("transaction item")
        verbose_name_plural = _("transaction items")

    def __unicode__(self):
        return self.category.name


class Transaction(Movement):
    items = models.ManyToManyField("ItemCategory", through="TransactionItem", verbose_name=_("items"))
    source = models.ForeignKey("Place", verbose_name=_("source"), related_name="transaction_sources")
    destination = models.ForeignKey("Place", verbose_name=_("destination"), related_name="transaction_destinations")
    is_negotiated_source = models.BooleanField(_("source negotiated"), blank=True, default=False)
    is_negotiated_destination = models.BooleanField(_("destination negotiated"), blank=True, default=False)
    is_confirmed_source = models.BooleanField(_("source confirmed"), blank=True, default=False)
    is_confirmed_destination = models.BooleanField(_("destination confirmed"), blank=True, default=False)
    comment = models.TextField(_("comment"), blank=True, null=True)
    comment_places = models.ManyToManyField("Place", verbose_name=_("comment places"))

    # Movement superclass
    # created_at = models.DateTimeField(_("created at"), default=timezone.now)
    # completed_at = models.DateTimeField(_("completed at"), default=None, blank=True, null=True)
    # is_completed = models.BooleanField(_("is completed"), blank=True, default=False)
    # is_prepared = models.BooleanField(_("is prepared"), blank=True, default=False)

    class Meta:
        verbose_name = _("transaction")
        verbose_name_plural = _("transaction")

    def __unicode__(self):
        return u'%s → %s' % (self.source.name, self.destination.name)

    def reset(self):
        self.is_prepared = False
        self.is_negotiated_source = False
        self.is_negotiated_destination = False
        self.is_confirmed_source = False
        self.is_confirmed_destination = False
        for trans_item in self.transaction_items.all():
            try:
                item = Item.objects.get(reserved_by=trans_item)
            except Item.DoesNotExist:
                pass
            else:
                if item.parent:
                    item.parent.deposit(item)
                else:
                    self.source.deposit(item)

    @transaction.atomic
    def prepare(self):
        self.items_prepared = []
        for trans_item in self.transaction_items.all():
            try:
                item = Item.objects.get(reserved_by=trans_item)
            except Item.DoesNotExist:
                item = self.source.withdraw(trans_item)
                item.is_reserved = True
                item.reserved_by = trans_item
                item.save()
        self.is_prepared = True

    def check_prepared(self):
        self.items_prepared = []
        self.transaction_items.filter(destination__isnull=True).update(destination=self.destination)
        for ti in self.transaction_items.all():
            item = ti.item_set.get()
            assert (ti.transaction == self)
            assert (item.quantity == ti.quantity)
            assert (item.category == ti.category)
            assert (item.place == ti.transaction.source)
            self.items_prepared.append(item)

    def force_complete(self):
        self.is_negotiated_source = True
        self.is_negotiated_destination = True
        self.is_confirmed_source = True
        self.is_confirmed_destination = True
        self.complete()

    @transaction.atomic
    def complete(self):
        if self.is_completed:
            return
        if not self.is_prepared:
            self.prepare()
        self.check_prepared()
        if not self.is_negotiated_source:
            raise TransactionNotReady(_("list is not confirmed by source"))
        if not self.is_negotiated_destination:
            raise TransactionNotReady(_("list is not confirmed by destination"))
        if not self.is_confirmed_source:
            raise TransactionNotReady(_("transaction is not confirmed by source"))
        if not self.is_confirmed_destination:
            raise TransactionNotReady(_("transaction is not confirmed by destination"))
        for item in self.items_prepared:
            if item.reserved_by.destination:
                assert item.reserved_by.destination.is_descendant_of(self.destination, include_self=True), ugettext(
                    "<{ti_dest}> must be child node of <{dest}>".format(
                                ti_dest=unicode(item.reserved_by.destination.name),
                                dest=unicode(self.destination.name)
                            )
                )
                item.reserved_by.destination.deposit(item)
            else:
                self.destination.deposit(item)
        self.is_completed = True
        self.completed_at = timezone.now()
        self.save()


class ProcessSerialMixin(object):

    def __init__(self):
        self.void = Place.objects.get(pk=74)
        self.item = self.item or {}
        self.serial = self.serial or ""

    @transaction.atomic
    def process(self):
        assert self.item.place.pk in get_descendants_ids(Place, 14)
        tr = Transaction.objects.create(source=self.item.place, destination=self.void)
        TransactionItem.objects.create(transaction=tr, quantity=1, category=self.item.category, serial=self)
        tr.force_complete()


def get_descendants_ids(model, pk, include_self=False):
    try:
        obj = model.objects.get(pk=pk)
    except model.DoesNotExist:
        ids = []
    else:
        ids = obj.get_descendants(include_self=include_self).values_list('id', flat=True)
    return ids


class OrderItemSerial(ItemSerial, ProcessSerialMixin):
    class Meta:
        proxy = True
        verbose_name = _("order serial")
        verbose_name_plural = _("order serials")

class ContractItemSerial(ItemSerial, ProcessSerialMixin):
    class Meta:
        proxy = True
        verbose_name = _("contract serial")
        verbose_name_plural = _("contract serials")


class VItemMovement(models.Model):
    """
     item_category_name | character varying(100)   |           | extended |
     source_name        | character varying(100)   |           | extended |
     destination_name   | character varying(100)   |           | extended |
     quantity           | numeric                  |           | main     |
     destination_id     | integer                  |           | plain    |
     source_id          | integer                  |           | plain    |
     transaction_item_id | integer                  |           | plain    |
     category_id        | integer                  |           | plain    |
     transaction_id     | integer                  |           | plain    |
     created_at         | timestamp with time zone |           | plain    |
     completed_at       | timestamp with time zone |           | plain    |
    """
    item_category_name = models.CharField(_("item_category"), max_length=100)
    source_name = models.CharField(_("source"), max_length=100)
    destination_name = models.CharField(_("destination"), max_length=100)
    quantity = models.DecimalField(_("quantity"), max_digits=9, decimal_places=3)
    source = models.ForeignKey("Place", verbose_name=_("source"), related_name="source_item_movements", on_delete=models.DO_NOTHING)
    transaction_item = models.OneToOneField("TransactionItem", verbose_name=_("transaction_item"), on_delete=models.DO_NOTHING, primary_key=True)
    destination = models.ForeignKey("Place", verbose_name=_("destination"), related_name="destination_item_movements", on_delete=models.DO_NOTHING)
    category = models.ForeignKey("ItemCategory", verbose_name=_("item category"), on_delete=models.DO_NOTHING)
    transaction = models.ForeignKey("Transaction", verbose_name=_("transaction"), on_delete=models.DO_NOTHING)
    created_at = models.DateTimeField(_("created at"), default=timezone.now)
    completed_at = models.DateTimeField(_("completed at"), default=None, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "base_v_item_movement"
        verbose_name = _("item movement")
        verbose_name_plural = _("items movements")
        ordering = ['-created_at']

    def __unicode__(self):
        return self.item_category_name


class VSerialMovement(models.Model):
    """
     source         | character varying(100)   |           | extended |
     destination    | character varying(100)   |           | extended |
     item_category  | character varying(100)   |           | extended |
     quantity       | numeric(9,3)             |           | main     |
     destination_id | integer                  |           | plain    |
     source_id      | integer                  |           | plain    |
     category_id    | integer                  |           | plain    |
     transaction_id | integer                  |           | plain    |
     serial         | character varying(32)    |           | extended |
     serial_id      | integer                  |           | plain    |
     created_at     | timestamp with time zone |           | plain    |
     completed_at   | timestamp with time zone |           | plain    |
    """

    item_category_name = models.CharField(_("item_category"), max_length=100)
    source_name = models.CharField(_("source"), max_length=100)
    destination_name = models.CharField(_("destination"), max_length=100)
    quantity = models.DecimalField(_("quantity"), max_digits=9, decimal_places=3)
    serial = models.CharField(_("serial"), max_length=32)
    serial_id = models.OneToOneField("ItemSerial", verbose_name=_("serial"), db_column="serial_id", on_delete=models.DO_NOTHING, primary_key=True)
    source = models.ForeignKey("Place", verbose_name=_("source"), related_name="source_serial_movements", on_delete=models.DO_NOTHING)
    destination = models.ForeignKey("Place", verbose_name=_("destination"), related_name="destination_serial_movements", on_delete=models.DO_NOTHING)
    category = models.ForeignKey("ItemCategory", verbose_name=_("item category"), on_delete=models.DO_NOTHING)
    transaction = models.ForeignKey("Transaction", verbose_name=_("transaction"), on_delete=models.DO_NOTHING)
    created_at = models.DateTimeField(_("created at"), default=timezone.now)
    completed_at = models.DateTimeField(_("completed at"), default=None, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "base_v_serial_movement"
        verbose_name = _("serial movement")
        verbose_name_plural = _("serials movements")
        ordering = ['-created_at']

    def __unicode__(self):
        return self.item_category_name