# -*- encoding: utf-8 -*-
from __future__ import print_function, division, unicode_literals, absolute_import

from decimal import Decimal

from django.db import models, IntegrityError
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _, ugettext
from django.contrib.staticfiles.templatetags.staticfiles import static
from mptt.models import MPTTModel
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import transaction
from django.conf import settings
from filebrowser.fields import FileBrowseField
from sorl.thumbnail import get_thumbnail
import re
from copy import copy

from base.decorators import lazyprop


class Object(object):
    pass


class IncompatibleUnitException(ValueError):
    """
    Thrown when you are trying to store or withdraw decimal amount from
    item that can have only integer amount.
    """
    pass


class ItemNotFound(ValueError):
    """
    Thrown when you try to withdraw Item from Place but there is not any available.
    """
    pass


class QuantityNotEnough(ValueError):
    """
    Thrown when you try to withdraw Item from Place but there are no enough quantity available
    """
    pass


class InvalidParameters(ValueError):
    """
    Thrown when function expects other type arguments
    """
    pass


class DryRun(RuntimeError):
    """
    Thrown when dry_run argument is passed to operation. With atomic requests it will rollback operation.
    Useful for testing purposes
    """
    pass


class TransactionNotReady(RuntimeError):
    """
    Thrown when transaction.complete is called but transaction does not have all 2-step handshake flags:
    is_negotiated_source
    is_negotiated_destination
    is_confirmed_source
    is_confirmed_destination
    :note: Now all transaction are managed by storage operator and Transaction.force_complete method
           ignores all this flags.
    """
    pass


def get_placeholder_image():
    """
    Returns empty image for placeholders. Path is set in settings.PLACEHOLDER_IMAGE_PATH
    :return: Placeholder image object
    :rtype: ImageFile
    """
    from django.core.files.images import ImageFile
    from django.core.files.storage import get_storage_class
    storage_class = get_storage_class(settings.STATICFILES_STORAGE)
    storage = storage_class()
    placeholder = storage.open(settings.PLACEHOLDER_IMAGE_PATH)
    image = ImageFile(placeholder)
    image.storage = storage
    return image


class GeoName(models.Model):
    """
    Model with geographical names, cities, villages, streets...
    Used in validation process for Place.name
    """
    name = models.CharField(max_length=100, unique=True)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name


class Unit(models.Model):
    """
    Model with units.
    """
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

    def __str__(self):
        return self.name


class ItemCategory(MPTTModel):
    """
    Model with item categories. Tree-like structure is provided by django-mptt app
     - is_stackable - flag that shows if two chunks can be joined to whole one for this item category.
       Falce values are used for cables in example.
    """
    @staticmethod
    def get_upload_dir():
        return "uploads"

    name = models.CharField(_("name"), max_length=100, unique=True)
    unit = models.ForeignKey("Unit", verbose_name=_("unit"), blank=True, null=True)
    is_stackable = models.NullBooleanField(_("stackable"), blank=True, null=True)
    parent = models.ForeignKey('self', verbose_name=_("parent"), null=True, blank=True, related_name='children')
    comment = models.TextField(_("comment"), blank=True, null=True)
    photo = FileBrowseField("Image", max_length=200, directory=get_upload_dir, blank=True, null=True)
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = _("item category")
        verbose_name_plural = _("item categories")

    class MPTTMeta:
        order_insertion_by = ['name']

    def __str__(self):
        return self.name

    def clean_unit(self):
        """
        Validates ItemCategory.unit. If it is empty - value is taken from closest parent.
        Throws ValidationError if ItemCategory.unit is empty for this object and all of his parents.
        :return: None
        """
        obj = self
        while not obj.unit and obj.parent:
            obj = obj.parent
        if obj.unit:
            self.unit = obj.unit
        else:
            raise ValidationError({'unit': ugettext('Unit must be set for object or for one of its parents.')})

    def clean_is_stackable(self):
        """
        Validates ItemCategory.is_stackable. If it is empty - value is taken from closest parent.
        Throws ValidationError if ItemCategory.is_stackable is empty for this object and all of his parents.
        :return: None
        """
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

    @staticmethod
    def autocomplete_search_fields():
        return "id__iexact", "name__icontains",

    @property
    def thumbnail(self):
        """
        :return: ItemCategory.photo or placeholder if photo is not set.
        :rtype: ImageFile
        """
        im = get_thumbnail(self.photo or get_placeholder_image(), '128x128', crop='center', quality=99)
        return im

    @lazyprop
    def node_view_url(self):
        """
        Url for base_category_item_changelist admin page
        :return: url
        :rtype: string
        """
        return reverse("admin:base_category_item_changelist", args=[self.pk])

    def node_view_link(self):
        """
        Html code with link for base_category_item_changelist admin page
        :return: html code with link
        :rtype: string
        """
        return mark_safe('<a href="%s"><img src="%s" width="16" height="8" alt="%s"></a>' % (
            self.node_view_url,
            static("glyphicons/glyphicons-52-eye-open.png"),
            _("view"),
        ))

    """
    short_description for function is used as table header in admin page
    https://docs.djangoproject.com/en/1.10/ref/contrib/admin/#django.contrib.admin.ModelAdmin.list_display
    """
    node_view_link.short_description = mark_safe('<img src="%s" width="16" height="8" alt="%s">' % (
        static("glyphicons/glyphicons-52-eye-open.png"),
        _("view"),
    ))
    node_view_link.allow_tags = True

    @lazyprop
    def node_transfer_url(self):
        if self.items.count():
            return reverse("admin:base_item_movement_filtered_changelist", args=[0, self.pk])
        return ''

    def node_transfer_link(self):
        if self.node_transfer_url:
            return mark_safe('<a href="%s"><img src="%s" width="11" height="10" alt="%s"></a>' % (
                self.node_transfer_url,
                static("glyphicons/glyphicons-458-transfer.png"),
                _("view movement"),
            ))
        else:
            return ''

    node_transfer_link.short_description = mark_safe('<img src="%s" width="11" height="10" alt="%s">' % (
        static("glyphicons/glyphicons-458-transfer.png"),
        _("view movement"),
    ))
    node_transfer_link.allow_tags = True

    @lazyprop
    def node_storage_url(self):
        return reverse(
            'admin:base_place_item_changelist',
            args=(settings.APP_FILTERS["PLACE_STORAGE_ID"],)
        ) + "?category__id__in=%s" % self.pk

    def node_storage_link(self):
        return mark_safe('<a href="%s"><img src="%s" width="10" height="10" alt="%s"></a>' % (
            self.node_storage_url,
            static("glyphicons/glyphicons-157-show-thumbnails.png"),
            _("view storage"),
        ))

    node_storage_link.short_description = mark_safe('<img src="%s" width="10" height="10" alt="%s">' % (
        static("glyphicons/glyphicons-157-show-thumbnails.png"),
        _("view storage"),
    ))
    node_storage_link.allow_tags = True

    @lazyprop
    def node_tree_url(self):
        return "%s#ItemCategory/%s" % (reverse("admin:base_itemcategory_changelist"), self.pk)

    def node_tree_link(self):
        return mark_safe('<a href="%s"><img src="%s" width="13" height="15" alt="%s"></a>' % (
            self.node_tree_url,
            static("glyphicons/glyphicons-427-git-merge.png"),
            _("view in tree"),
        ))

    node_tree_link.short_description = mark_safe('<img src="%s" width="13" height="15" alt="%s">' % (
        static("glyphicons/glyphicons-427-git-merge.png"),
        _("view in tree"),
    ))
    node_tree_link.allow_tags = True


class ItemCategoryComment(models.Model):
    """
    Model for additional ItemCategory data. Used serial keys generation and barcode printing
    """
    category = models.ForeignKey("ItemCategory", verbose_name=_("item category"), related_name="comments")
    serial_prefix = models.CharField(max_length=12, verbose_name=_("prefix"), unique=True)
    serial_last_code = models.CharField(max_length=12, verbose_name=_("last code"), blank=True, null=True)
    comment = models.CharField(max_length=100, verbose_name=_("comment"), blank=True, null=True)

    class Meta:
        verbose_name = _("item category comment")
        verbose_name_plural = _("item category comments")

    def __str__(self):
        return "%s - %s" % (self.category.name, self.serial_prefix)


class Place(MPTTModel):
    """
    Model with places. Tree-like structure is provided by django-mptt app.
     - is_shop: flag that allows item creation from nothing in this place. Used in Purchase with auto_source.
     - has_cells: not used yet.
     - has_chunks:
        if Transaction.destination = this place and ItemCategory.is_stackable is False for
        TransactionItem, then ItemChunk will be created in this place.
        if Transaction.source = this place and ItemCategory.is_stackable is False for
        TransactionItem, then ItemChunk should be set for TransactionItem.
        Its quantity will change and if it drops to zero - ItemChunk will be deleted.
    """
    name = models.CharField(_("name"), max_length=100, unique=True)
    parent = models.ForeignKey('self', verbose_name=_("parent"), null=True, blank=True, related_name='children')
    is_shop = models.BooleanField(_("is shop"), blank=True, default=False)
    has_cells = models.BooleanField(_("has cells"), default=False)
    has_chunks = models.BooleanField(_("has chunks"), default=False)
    comment = models.TextField(_("comment"), blank=True, null=True)
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = _("place")
        verbose_name_plural = _("places")
        unique_together = (
            ('name', 'parent'),
        )
        # Permissions not used yet. they are designed for full 2-step handshake transactions.
        # Now transactions are managed by storage operator.
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

    def __str__(self):
        return self.name

    def clean_name(self):
        pass

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Place, self).save(*args, **kwargs)

    def get_absolute_url(self):
        """
        url for admin interface
        :return: url
        :rtype: str
        """
        return reverse('admin:base_place_item_changelist', args=[self.pk])

    def deposit(self, item, cell=None):
        """
        Stores item in this place.
        If in this place exists item with the same ItemCategory - Item.deposit method will be called to join
          two items into single one.
        If in this place no item with the same ItemCategory - item.place can be safely changed into this place.
        :param item: Item that will be stored in this place
        :type item: Item
        :param cell: If not null - Item.cell will be set to this value.
        :type cell: str
        :return: None
        """
        try:
            i = self.items.get(category=item.category, is_reserved=False)
        except Item.DoesNotExist:
            item.place = self
            item.is_reserved = False
            item.reserved_by = None
            item.parent = None
            item.cell = cell
            item.save()
            if self.has_chunks and not item.is_stackable:
                if not item.chunks.count():
                    ItemChunk.objects.create(item=item, chunk=item.quantity, purchase=item.purchase, cell=cell)
        else:
            new_item = i.deposit(item, cell=cell)

            if not self.has_chunks:
                new_item.chunks.all().delete()

    def withdraw(self, item):
        """
        Removes Item from this place. Function finds Item with the same ItemCategory in this place and calls
        Item.withdraw
        :param item: Item which is needed to be removed from this place
        :type item: Item
        :return: new Item.
        :rtype: Item
        """
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
                    raise InvalidParameters(
                        _("Can not withdraw <{item}> from <{place}>: quantity >1 for serial <{serial}> ".format(
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
                serial.cell = None
                serial.save()
            return i.withdraw(quantity=item.quantity, serial=serial, chunk=item.chunk)

    def join_to(self, place):
        """
        Helper function to join contents of 2 places into one. It creates transaction from this place to provided place
        and all stored items are moved to provided place by this transaction.
        This place name will be marked with DEL prefix and can be safely deleted in future by storage manager.
        :param place:
        :type place: Place
        :return: None
        """
        t = Transaction.objects.create(source=self, destination=place)
        for item in self.items.filter(quantity__gt=0):
            if item.serials.count():
                for serial in item.serials.all():
                    TransactionItem.objects.create(transaction=t, category=item.category, quantity=1, serial=serial)
            else:
                TransactionItem.objects.create(transaction=t, category=item.category, quantity=item.quantity)
        t.force_complete()
        Transaction.objects.filter(source=self).update(source=place)
        Transaction.objects.filter(destination=self).update(destination=place)
        TransactionItem.objects.filter(destination=self).update(destination=place)
        Purchase.objects.filter(source=self).update(source=place)
        Purchase.objects.filter(destination=self).update(destination=place)
        Item.objects.filter(place=self, quantity=0).delete()
        self.name = "DEL %s" % self.name
        self.save()

    @staticmethod
    def autocomplete_search_fields():
        return "id__iexact", "name__icontains",

    @lazyprop
    def node_view_url(self):
        if self.items.count():
            return reverse("admin:base_place_item_changelist", args=[self.pk])
        else:
            return ''

    def node_view_link(self):
        if self.node_view_url:
            return mark_safe('<a href="%s"><img src="%s" width="16" height="8" alt="%s"></a>' % (
                self.node_view_url,
                static("glyphicons/glyphicons-52-eye-open.png"),
                _("view"),
            ))
        else:
            return ''

    node_view_link.short_description = mark_safe('<img src="%s" width="16" height="8" alt="%s">' % (
        static("glyphicons/glyphicons-52-eye-open.png"),
        _("view"),
    ))
    node_view_link.allow_tags = True

    @lazyprop
    def node_transfer_url(self):
        if self.items.count():
            return reverse("admin:base_item_movement_filtered_changelist", args=[self.pk])
        return ''

    def node_transfer_link(self):
        if self.node_transfer_url:
            return mark_safe('<a href="%s"><img src="%s" width="11" height="10" alt="%s"></a>' % (
                self.node_transfer_url,
                static("glyphicons/glyphicons-458-transfer.png"),
                _("view movement"),
            ))
        else:
            return ''

    node_transfer_link.short_description = mark_safe('<img src="%s" width="11" height="10" alt="%s">' % (
        static("glyphicons/glyphicons-458-transfer.png"),
        _("view movement"),
    ))
    node_transfer_link.allow_tags = True

    @lazyprop
    def node_tree_url(self):
        return "%s#Place/%s" % (reverse("admin:base_place_changelist"), self.pk)

    def node_tree_link(self):
        return mark_safe('<a href="%s"><img src="%s" width="13" height="15" alt="%s"></a>' % (
            self.node_tree_url,
            static("glyphicons/glyphicons-427-git-merge.png"),
            _("view in tree"),
        ))

    node_tree_link.short_description = mark_safe('<img src="%s" width="13" height="15" alt="%s">' % (
        static("glyphicons/glyphicons-427-git-merge.png"),
        _("view in tree"),
    ))
    node_tree_link.allow_tags = True


class MovementItem(models.Model):
    """
    Abstract class for TransactionItem and PurchaseItem.
    Common fields and functions placed here
    """
    category = models.ForeignKey("ItemCategory", verbose_name=_("item category"))
    quantity = models.DecimalField(_("quantity"), max_digits=9, decimal_places=3)

    # _chunks = models.TextField(blank=True, null=True)

    class Meta:
        abstract = True

    # def clean_chunks(self):
    #     if not self._chunks:
    #         return []
    #
    #     chunks_str = re.findall(r"[\d\.]+", self._chunks)
    #     f = None
    #     if self.category.unit.unit_type == Unit.INTEGER:
    #         f = int
    #     if self.category.unit.unit_type == Unit.DECIMAL:
    #         f = Decimal
    #     if not f:
    #         raise ValidationError(ugettext("Category unit type is unknown"))
    #     try:
    #         chunks_data = map(f, chunks_str)
    #     except Exception, e:
    #         raise ValidationError({'_chunks': ugettext('data error: %s' % e)})
    #     total = reduce(lambda x, y: f(x + y), chunks_data, 0)
    #     if not total == self.quantity:
    #         raise ValidationError({
    #             '_chunks': ugettext(u'chunks sum error: {total}≠{quantity}'.format(
    #                 total=total,
    #                 quantity=self.quantity
    #             ))
    #         })
    #     self._chunks = ", ".join(map(str, chunks_data))
    #     return chunks_data
    #
    # @property
    # def chunks(self):
    #     return self.clean_chunks()
    #
    # @chunks.setter
    # def chunks(self, value):
    #     self._chunks = ", ".join(value)

    def clean_quantity(self):
        try:
            self.category
        except ItemCategory.DoesNotExist:
            raise ValidationError({'category': ugettext(
                'this field is required'
            )})
        f = None
        if self.category.unit.unit_type == Unit.INTEGER:
            f = int
        if self.category.unit.unit_type == Unit.DECIMAL:
            f = Decimal

        if self.quantity and not f(self.quantity) == self.quantity:
            raise ValidationError({'quantity': ugettext(
                'unit type `%s` can not be decimal' % self.category.unit.name
            )})

    def clean(self):
        self.clean_quantity()
        # self.clean_chunks()

    def save(self, *args, **kwargs):
        self.full_clean()
        super(MovementItem, self).save(*args, **kwargs)


class PurchaseItem(MovementItem):
    """
    M2M Model for Purchase and ItemCategory relations
    Purchase.items = models.ManyToManyField("ItemCategory", through="PurchaseItem" ...)
    """
    purchase = models.ForeignKey("Purchase", verbose_name=_("Purchase"), related_name="purchase_items")
    price = models.DecimalField(_("price"), max_digits=9, decimal_places=2)
    price_usd = models.DecimalField(_("price usd"), max_digits=9, decimal_places=2, blank=True, null=True)
    # Movement superclass
    # category = models.ForeignKey("ItemCategory", verbose_name=_("item category"))
    # quantity = models.DecimalField(_("quantity"), max_digits=9, decimal_places=3)
    _serials = models.TextField(blank=True, null=True)
    # _chunks = models.TextField(blank=True, null=True)
    cell = models.CharField(max_length=16, blank=True, null=True)

    class Meta:
        verbose_name = _("purchase item")
        verbose_name_plural = _("purchase items")
        permissions = (
            ('view_item_price', _('view item price')),  # can view price
        )

    def __str__(self):
        if self.purchase.completed_at:
            return u"%s: %s, %s → %s" % (
                self.purchase.completed_at.strftime("%Y-%m-%d"),
                self.category.name,
                self.purchase.source,
                self.purchase.destination
            )
        return u" --- %s, %s → %s" % (
            self.category.name,
            self.purchase.source,
            self.purchase.destination
        )

    def clean_serials(self):
        """
        Validation for _serials value. Multiple serials can be provided with any delimiter except dash ("-").
        If _serials count does not match with Item.quantity then Validation error raises
        :return: list of serials
        :rtype: list[str]
        """
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
        """
        getter method for serials
        :return: list of serials
        :rtype: list[str]
        """
        return self.clean_serials()

    @serials.setter
    def serials(self, value):
        """
        setter method for serials
        :return: None
        """
        self._serials = ", ".join(value)

    def clean(self):
        self.clean_serials()

    def save(self, *args, **kwargs):
        self.full_clean()
        super(PurchaseItem, self).save(*args, **kwargs)


class Payer(models.Model):
    """
    Model with purchase payer name. Used in Purchase.payer
    """
    name = models.CharField(_("payer"), max_length=100)

    class Meta:
        verbose_name = _("payer")
        verbose_name_plural = _("payers")

    def __str__(self):
        return self.name


class Movement(models.Model):
    """
    Abstract class for Transaction and Purchase
    Common fields and functions placed here
    """
    items_prepared = []
    created_at = models.DateTimeField(_("created at"), default=timezone.now)
    completed_at = models.DateTimeField(_("completed at"), default=None, blank=True, null=True)
    is_completed = models.BooleanField(_("is completed"), blank=True, default=False)
    is_prepared = models.BooleanField(_("is prepared"), blank=True, default=False)

    class Meta:
        abstract = True


class Purchase(Movement):
    """
    Model for registering purchases from shops.
     - is_auto_source: if True, Items will be created in source Place. (True in 100% purchases =) )
    """
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

    def __str__(self):
        if self.completed_at:
            return u'%s: %s → %s' % (self.completed_at.strftime("%Y-%m-%d"), self.source.name, self.destination.name)
        else:
            return u'--- %s → %s' % (self.source.name, self.destination.name)
            # return u'%s -> %s' % (self.source.name, self.destination.name)

    def clean_is_auto_source(self):
        """
        is_auto_source can be set true only if source Place.is_shop is True too
        :return: None
        """
        if self.source_id:
            if self.is_auto_source and not self.source.is_shop:
                raise ValidationError({'is_auto_source': ugettext('auto source is allowed for shops only')})

    def clean(self):
        self.clean_is_auto_source()

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Purchase, self).save(*args, **kwargs)

    def prepare_items_auto(self):
        """
        Creates new items in source. If called more than once - items from previous preparation are removed.
        :return: None
        """
        self.items_prepared = []
        self.is_prepared = False
        for purchase_item in self.purchase_items.all():
            purchase_item.item_set.all().delete()
            i, created = Item.objects.get_or_create(category=purchase_item.category, place=self.source,
                                                    purchase=purchase_item)
            if created:
                i.quantity = purchase_item.quantity
                i.purchase = purchase_item
                i.save()
            else:
                Item.objects.filter(pk=i.pk).update(quantity=models.F('quantity') + purchase_item.quantity)
                i.refresh_from_db()
            # if purchase_item.chunks:
            #     for chunk in purchase_item.chunks:
            #         ItemChunk.objects.create(item=i, chunk=chunk, purchase=purchase_item)
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
                                item_serial.item.__str__(),
                                item_serial.item.place.__str__() if item_serial.item.place else None,
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
    def complete(self, pending=False):
        """
        Completes this Purchase. Process steps are:
          - check pending, if it's True - ignore and let PurchaseItems be saved first
          - check already completed. If true - ignore
          - prepare items ( see Purchase.prepare_items_auto)
          - create new transaction, source is purchase source, destination is purchase destination, items ... the same
        :param pending: flag, if True then formset with PurchaseItems is not saved yet
        :type pending: bool
        :return: None
        """
        if pending:
            # print "purchase complete defer"
            setattr(self, "is_pending", True)
            return
        # print "purchase complete run"
        if self.is_completed:
            return
        self.prepare()
        prepared = self.is_prepared
        t = Transaction.objects.create(source=self.source, destination=self.destination)
        for pi in self.purchase_items.all():

            if not pi.serials:
                ti = TransactionItem.objects.create(purchase=self, transaction=t, category=pi.category,
                                                    quantity=pi.quantity, serial=None, cell=pi.cell,
                                                    destination=self.destination)  # noqa

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
                                                        quantity=1, serial=s, cell=pi.cell)  # noqa

        t.is_prepared = prepared
        t.is_negotiated_source = True
        t.is_negotiated_destination = True
        t.is_confirmed_source = True
        t.is_confirmed_destination = True
        t.complete()

        self.completed_at = timezone.now()
        self.is_completed = True
        self.save()
        # self.fill_cells()

    def fill_cells(self):
        """
        Update Item.cell and ItemSerial.cell values if PurchaseItem.cell is set.
        creates new objects in Cell model if does not exist
        :return: None
        """
        for pi in self.purchase_items.all():
            place = pi.purchase.destination
            if not place.has_cells or not pi.cell:
                continue
            else:
                cell, created = Cell.objects.get_or_create(place_id=place.id, name=pi.cell)
                pi.item_set.update(cell=cell)
                ItemSerial.objects.filter(item__pk__in=pi.item_set.values_list("pk", flat=True)).update(cell=cell)


class Item(models.Model):
    """
    Model for items
     - is_reserved: Is True if this item is created for transaction (after Item.withdraw for example)
     - reserved_by: FK to TransactionItem which reserves this item for transaction.
    """
    category = models.ForeignKey("ItemCategory", verbose_name=_("item category"), related_name='items')
    quantity = models.DecimalField(_("quantity"), max_digits=9, decimal_places=3, default=0)
    is_reserved = models.BooleanField(_("is reserved"), blank=True, default=False)
    reserved_by = models.ForeignKey("TransactionItem", verbose_name=_("reserved by transaction"), blank=True, null=True)
    parent = models.ForeignKey('self', verbose_name=_("parent"), blank=True, null=True, related_name="children")
    place = models.ForeignKey("Place", verbose_name=_("place"), blank=True, null=True, related_name='items')
    purchase = models.ForeignKey("PurchaseItem", verbose_name=_("purchase"), blank=True, null=True)
    comment = models.TextField(_("comment"), blank=True, null=True)
    cell = models.ForeignKey("Cell", blank=True, null=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name = _("item")
        verbose_name_plural = _("items")

    def __str__(self):
        if self.place:
            return "%s - %s" % (self.category.name, self.place.name)
        return "%s - unknown place" % self.category.name

    def category_name(self):
        return self.category.name

    def get_absolute_url(self):
        return reverse('admin:base_item_serials_filtered_changelist', args=[self.pk])

    @property
    def unit(self):
        return self.category.unit

    @property
    def is_stackable(self):
        return self.category.is_stackable

    @property
    def price(self):
        if self.purchase:
            if self.purchase.price_usd:
                return "%s UAH (%s USD)" % (self.purchase.price, self.purchase.price_usd)
            else:
                return "%s UAH" % (self.purchase.price,)
        return "?"

    def clean_quantity(self):
        """
        Item.quantity validator. Checks unit type to decide if value can be decimal
        :return: None
        """
        f = int
        # if self.category.unit.unit_type == Unit.INTEGER:
        #     f = int
        if self.category.unit.unit_type == Unit.DECIMAL:
            f = Decimal

        if self.quantity and not f(self.quantity) == self.quantity:
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
        """
        Used for calling function qs.update for atomic operations. Set value then call save is not thread safe.
        As alternative models.F can be used when setting value, but getting value then is
        not possible w/o re-fetching object from db.
        :return: QuerySet with single object (this object).
        """
        return self.__class__.objects.filter(pk=self.pk)

    # noinspection DjangoOrm
    def withdraw_any(self, quantity):
        """
        Splits item into two. Requested quantity is subtracted from this object.
        :param quantity: Amount of items to withdraw
        :type quantity: int or Decimal
        :returns: Item created in result of withdrawal spit request.
                  Marked as reserved until transaction will be completed or cancelled
        :rtype: base.models.Item()
        """

        if self.quantity - self.serials.count() < quantity:
            raise InvalidParameters(_("please provide serial to withdraw"))
        if self.place.has_chunks:
            if self.chunks.count() == 1:
                return self.withdraw_chunk(quantity, self.chunks.get())
            if self.chunks.count() > 1:
                total_chunks_len = self.chunks.aggregate(models.Sum('chunk'))['chunk__sum']
                if self.quantity - total_chunks_len < quantity:
                    raise InvalidParameters(_("please provide chunk to withdraw"))
        else:
            self.chunks.all().delete()
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
        Splits item into two. Requested quantity is subtracted from this object
        and provided serial is moved to the new item.
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
                item=self.__str__()
            )))
        item = Item.objects.create(
            quantity=quantity,
            is_reserved=True,
            purchase=self.purchase,
            category=self.category,
            place=self.place,
            parent=self,
        )
        serial.item = item
        serial.save()
        return item

    def withdraw_chunk(self, quantity, chunk):
        """
        Splits item into two. Requested quantity is subtracted from this object and provided chunk.
        :param quantity: Amount of items to withdraw
        :type quantity: int or Decimal
        :param chunk: instance of base.models.ItemChunk
        :type chunk: base.models.ItemChunk()
        :returns: Item created in result of withdrawal spit request.
                  Marked as reserved until transaction will be completed or cancelled
                  And two chunks: old one and new one.
        :rtype: tuple[Item, Chunk, Chunk]
        """
        if chunk.chunk < quantity:
            raise InvalidParameters(_("Chunks length lesser than requested quantity"))
        item = Item.objects.create(
            quantity=quantity,
            is_reserved=True,
            purchase=self.purchase,
            category=self.category,
            place=self.place,
            parent=self,
        )
        if chunk.chunk == quantity:
            chunk.qs.update(item=item)
            chunk_b = None
        else:
            chunk.qs.update(chunk=models.F('chunk') - quantity)

            chunk_b = ItemChunk.objects.create(
                item=item,
                chunk=quantity,
                purchase=chunk.purchase
            )

        return item, chunk, chunk_b

    @transaction.atomic
    def withdraw(self, quantity, serial=None, chunk=None, dry_run=False):
        """
        Splits item into two. Requested quantity is subtracted from this object.
        If serial or chunk is provided alternative functions will be called.
        :param quantity: Amount of items to withdraw
        :type quantity: int or Decimal
        :param serial: optional, instance of base.models.ItemSerial
        :type serial: base.models.ItemSerial()
        :param chunk: optional, instance of base.models.ItemChunk
        :type chunk: base.models.ItemChunk()
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

        chunk_a = None
        chunk_b = None

        if serial:
            item = self.withdraw_serial(quantity, serial)
        elif chunk:
            item, chunk_a, chunk_b = self.withdraw_chunk(quantity, chunk)
        else:
            item = self.withdraw_any(quantity)

        self.qs.update(quantity=models.F('quantity') - quantity)
        self.refresh_from_db()

        if False:  # temporary disable check block
            if chunk_a:
                i = chunk_a.item
                i_chunk_len = i.chunks.aggregate(score=models.Sum('chunk'))['score']
                assert i.quantity == i_chunk_len, "Item chunk length error: %s %s <> %s" % (i, i.quantity, i_chunk_len)

            if chunk_b:
                i = chunk_b.item
                i_chunk_len = i.chunks.aggregate(score=models.Sum('chunk'))['score']
                assert i.quantity == i_chunk_len, "Item chunk length error: %s %s <> %s" % (i, i.quantity, i_chunk_len)

            if chunk_a or chunk_b:
                i = self
                i_chunk_len = i.chunks.aggregate(score=models.Sum('chunk'))['score']
                assert i.quantity == i_chunk_len, "Item chunk length error: %s %s <> %s" % (i, i.quantity, i_chunk_len)

        # if self.quantity == 0:
        # self.children.update(parent=None)
        # self.delete()

        if dry_run:
            raise DryRun(_("Cancelled due to dry_run option"))

        return item

    @transaction.atomic
    def deposit(self, item, dry_run=False, cell=None):
        """
        Joins item from args with self. Serials and Chunks are moving to new item too.
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
                ItemChunk.objects.create(item=item, chunk=item.quantity, purchase=item.purchase, cell=cell)
            if not self.chunks.count():
                ItemChunk.objects.create(item=self, chunk=self.quantity, purchase=self.purchase, cell=cell)

        if cell:
            if not item.cell == cell:
                if item.cell:
                    new_cell = Cell.objects.get_or_create(place=cell.place, name="%s+%s" % (item.cell.name, cell.name))
                else:
                    new_cell = cell
                self.qs.update(cell=new_cell)

        self.qs.update(quantity=models.F('quantity') + item.quantity, )
        self.refresh_from_db()

        if self.place and not self.place.has_chunks:
            item.chunks.all().delete()
        else:
            item.chunks.update(item=self)

        item.serials.update(item=self)

        item.delete()

        if dry_run:
            raise DryRun(_("Cancelled due to dry_run option"))

        return self


class ItemSerial(models.Model):
    """
    Model for storing items serials.
    """
    item = models.ForeignKey("Item", verbose_name=_("item"), related_name='serials')
    serial = models.CharField(_("serial"), max_length=32, unique=True)
    purchase = models.ForeignKey("PurchaseItem", verbose_name=_("purchase"), blank=True, null=True)
    comment = models.TextField(_("comment"), blank=True, null=True)
    cell = models.ForeignKey("Cell", blank=True, null=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name = _("serial")
        verbose_name_plural = _("serials")

    def __str__(self):
        return self.serial

    def category_name(self):
        return self.item.category.name

    @property
    def price(self):
        if self.purchase:
            if self.purchase.price_usd:
                return "%s UAH (%s USD)" % (self.purchase.price, self.purchase.price_usd)
            else:
                return "%s UAH" % (self.purchase.price,)
        return "?"

    def delete(self, using=None):
        raise NotImplementedError("Delete of serial numbers is not allowed!")


class ItemChunk(models.Model):
    """
    Model for storing items chunks.
    """
    item = models.ForeignKey("Item", verbose_name=_("item"), related_name='chunks')
    chunk = models.DecimalField(max_digits=9, decimal_places=3)
    label = models.CharField(_("label"), max_length=32, unique=True, blank=True, null=True)
    purchase = models.ForeignKey("PurchaseItem", verbose_name=_("purchase"), blank=True, null=True)
    cell = models.ForeignKey("Cell", blank=True, null=True, on_delete=models.SET_NULL)
    comment = models.TextField(_("comment"), blank=True, null=True)

    class Meta:
        verbose_name = _("chunk")
        verbose_name_plural = _("chunks")

    def __str__(self):
        return "ID_%s: %s %s%s" % (self.pk, self.chunk, self.item.unit, (" %s" % self.label) if self.label else "")

    def category_name(self):
        return self.item.category.name

    def place_name(self):
        return self.item.place.name

    @property
    def qs(self):
        return self.__class__.objects.filter(pk=self.pk)


class TransactionItem(MovementItem):
    """
    M2M Model for Transaction and ItemCategory relations
    Transaction.items = models.ManyToManyField("ItemCategory", through="TransactionItem" ...)
    """
    transaction = models.ForeignKey("Transaction", verbose_name=_("item transaction"), related_name="transaction_items")
    purchase = models.ForeignKey("Purchase", verbose_name=_("Purchase"),
                                 blank=True, null=True, related_name="transaction_items")
    purchase_item = models.ForeignKey("PurchaseItem", verbose_name=_("purchase"), blank=True, null=True)
    # Movement superclass
    # category = models.ForeignKey("ItemCategory", verbose_name=_("item category"))
    # quantity = models.DecimalField(_("quantity"), max_digits=9, decimal_places=3)
    # _chunks = models.TextField(blank=True, null=True)
    serial = models.ForeignKey(ItemSerial, blank=True, null=True, on_delete=models.SET_NULL)
    chunk = models.ForeignKey(ItemChunk, blank=True, null=True, on_delete=models.SET_NULL)
    destination = models.ForeignKey("Place", verbose_name=_("destination"),
                                    related_name="transaction_items", blank=True, null=True, on_delete=models.SET_NULL)
    cell_from = models.CharField(max_length=16, blank=True, null=True)
    cell = models.CharField(max_length=16, blank=True, null=True)

    class Meta:
        verbose_name = _("transaction item")
        verbose_name_plural = _("transaction items")

    def __str__(self):
        return self.category.name

    def clean_destination(self):
        trans = self.transaction
        if trans.destination_id == settings.APP_FILTERS['PLACE_ADDRESS_ID'] and hasattr(trans,
                                                                                        'is_pending') and trans.is_pending:
            if not self.destination:
                raise ValidationError(
                    {'destination': ugettext("Can't complete transaction because transaction item haven't destination")}
                )

    def clean(self):

        self.clean_destination()

    def save(self, *args, **kwargs):
        self.full_clean()
        if not self.cell_from:
            if self.serial:
                self.cell_from = self.serial.cell
            else:
                try:
                    item = Item.objects.get(place=self.transaction.source, category=self.category)
                except Item.DoesNotExist:
                    pass
                except Item.MultipleObjectsReturned:
                    pass
                else:
                    self.cell_from = item.cell
        super(TransactionItem, self).save(*args, **kwargs)


class Transaction(Movement):
    """
    Model for transactions, process for moving Items from source to destination (Places)
    .. note: flags is_negotiated_source, is_negotiated_destination, is_confirmed_source, is_confirmed_destination
             are not used yet, and were designed for full 2-step handshake transaction.
    """
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

    def __str__(self):
        return u'%s → %s' % (self.source.name, self.destination.name)

    def save(self, *args, **kwargs):
        super(Transaction, self).save(*args, **kwargs)

    def reset(self):
        """
        Resets status of transaction. If there are prepared items for this transaction - return them.
        :return: None
        """
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
        """
        Prepares items for moving into Destination place. new items are created by Place.withdraw (source)
        :return: None
        """
        self.items_prepared = []
        for trans_item in self.transaction_items.all():
            try:
                item = Item.objects.get(reserved_by=trans_item)
            except Item.DoesNotExist:
                item = self.source.withdraw(trans_item)
                item.is_reserved = True
                item.reserved_by = trans_item
                item.save()
            trans_item.purchase_item = item.purchase
            trans_item.save()
        self.is_prepared = True

    def check_prepared(self):
        """
        Check validity of prepared items. Set TransactionItem destination if it was not set before.
        :return: None
        """
        self.items_prepared = []
        self.transaction_items.filter(destination__isnull=True).update(destination=self.destination)
        for ti in self.transaction_items.all():
            item = ti.item_set.get()
            assert ti.transaction == self, ti.transaction
            assert item.quantity == ti.quantity, ti.quantity
            assert item.category == ti.category, ti.category
            assert item.place == ti.transaction.source, ti.transaction.source
            self.items_prepared.append(item)

    def force_complete(self, pending=False):
        """
        Ignores 2-step handshake and completes transaction w/o any conditions.
        :param pending: see Transaction.complete
        :type pending: bool
        :return: None
        """
        self.is_negotiated_source = True
        self.is_negotiated_destination = True
        self.is_confirmed_source = True
        self.is_confirmed_destination = True
        self.complete(pending)

    @transaction.atomic
    def complete(self, pending=False, transmutation=False):
        """
        Completes this Transaction. Process steps are:
          - check pending, if it's True - ignore and let TransactionItems be saved first
          - check already completed. If true - ignore
          - prepare items (see Transaction.prepare)
          - if not Transmutation - validate prepared items. For more info see base.models.Transmutation
          - deposit prepared items into destination Places
          - mark as completed and place timestamp
        :param pending: flag, if True then formset with TransactionItems is not saved yet
        :type pending: bool
        :return: None
        """
        if pending:
            # print "transaction complete defer"
            setattr(self, "is_pending", True)
            return
        # print "transaction complete run"
        if self.is_completed:
            return
        if not self.is_prepared:
            self.prepare()
        if not transmutation:
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

            cell = self.fill_cells(item.reserved_by)

            if item.reserved_by.destination:
                assert item.reserved_by.destination.is_descendant_of(self.destination, include_self=True), ugettext(
                    "<{ti_dest}> must be child node of <{dest}>".format(
                        ti_dest=item.reserved_by.destination.name,
                        dest=self.destination.name
                    )
                )
                item.reserved_by.destination.deposit(item, cell=cell)
            else:
                self.destination.deposit(item, cell=cell)
        self.is_completed = True
        self.completed_at = timezone.now()
        self.save()

    @staticmethod
    def fill_cells(ti):
        """
        Update Item.cell and ItemSerial.cell values if ti.cell is set.
        Creates new objects in Cell model, if it does not exist.
        :param ti: TransactionItem
        :type ti: TransactionItem
        :return: None
        """
        place = ti.destination or ti.transaction.destination
        if place.has_cells and ti.cell:
            cell, created = Cell.objects.get_or_create(place_id=place.id, name=ti.cell)
            ti.item_set.update(cell=cell)
            ItemSerial.objects.filter(item__pk__in=ti.item_set.values_list("pk", flat=True)).update(cell=cell)
            return cell
        return None


class ProcessSerialMixin(object):
    """
    Mixin class for movign item with specific serial key into Void place.
    """
    def __init__(self):
        self.void = Place.objects.get(pk=settings.APP_FILTERS["PLACE_VOID"])
        self.item = self.item or {}
        self.serial = self.serial or ""

    @transaction.atomic
    def process(self):
        assert self.item.place.pk in get_descendants_ids(Place, settings.APP_FILTERS["PLACE_WORKERS_ID"])
        tr = Transaction.objects.create(source=self.item.place, destination=self.void)
        TransactionItem.objects.create(transaction=tr, quantity=1, category=self.item.category, serial=self)
        tr.force_complete()


def get_descendants_ids(model, pk, include_self=False):
    """
    Helper function for MPTT models
    :param model: any MPTT model class
    :type model: MPTTModel
    :param pk: object's primary key in this model
    :type pk: int
    :param include_self: if True, specified id should be listed in result
    :type include_self: bool
    :return: list with id's - object's descendants
    :rtype: list[int]
    """
    try:
        obj = model.objects.get(pk=pk)
    except model.DoesNotExist:
        ids = []
    else:
        ids = obj.get_descendants(include_self=include_self).values_list('id', flat=True)
    return ids


class OrderItemSerial(ItemSerial, ProcessSerialMixin):
    """
    Proxy model for filtering ItemSerial only for specific ItemCategory
    See base.admin.OrderItemSerialAdmin
    """
    class Meta:
        proxy = True
        verbose_name = _("order serial")
        verbose_name_plural = _("order serials")


class ContractItemSerial(ItemSerial, ProcessSerialMixin):
    """
    Proxy model for filtering ItemSerial only for specific ItemCategory
    See base.admin.ContractItemSerialAdmin
    """
    class Meta:
        proxy = True
        verbose_name = _("contract serial")
        verbose_name_plural = _("contract serials")


class VItemMovement(models.Model):
    """
     Readonly model for display ing data from Postgresql's view.

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
    source = models.ForeignKey("Place", verbose_name=_("source"), related_name="source_item_movements",
                               on_delete=models.DO_NOTHING)
    transaction_item = models.OneToOneField("TransactionItem", verbose_name=_("transaction_item"),
                                            on_delete=models.DO_NOTHING, primary_key=True)
    destination = models.ForeignKey("Place", verbose_name=_("destination"), related_name="destination_item_movements",
                                    on_delete=models.DO_NOTHING)
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

    def __str__(self):
        return self.item_category_name

    @property
    def price(self):
        if self.transaction_item.purchase_item:
            purchase = self.transaction_item.purchase_item
            if purchase.price_usd:
                return "%s UAH (%s USD)" % (purchase.price, purchase.price_usd)
            else:
                return "%s UAH" % (purchase.price,)
        return "?"


class VSerialMovement(models.Model):
    """
     Readonly model for display ing data from Postgresql's view.

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
     transaction_item_id | integer                  |

    """

    transaction_item = models.OneToOneField("TransactionItem", verbose_name=_("transaction_item"),
                                            on_delete=models.DO_NOTHING, primary_key=True)
    item_category_name = models.CharField(_("item_category"), max_length=100)
    source_name = models.CharField(_("source"), max_length=100)
    destination_name = models.CharField(_("destination"), max_length=100)
    quantity = models.DecimalField(_("quantity"), max_digits=9, decimal_places=3)
    serial = models.CharField(_("serial"), max_length=32)
    serial_id = models.OneToOneField("ItemSerial", verbose_name=_("serial"), db_column="serial_id",
                                     on_delete=models.DO_NOTHING)
    source = models.ForeignKey("Place", verbose_name=_("source"), related_name="source_serial_movements",
                               on_delete=models.DO_NOTHING)
    destination = models.ForeignKey("Place", verbose_name=_("destination"), related_name="destination_serial_movements",
                                    on_delete=models.DO_NOTHING)
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

    def __str__(self):
        return self.item_category_name

    @property
    def price(self):
        if self.transaction_item.purchase_item:
            purchase = self.transaction_item.purchase_item
            if purchase.price_usd:
                return "%s UAH (%s USD)" % (purchase.price, purchase.price_usd)
            else:
                return "%s UAH" % (purchase.price,)
        return "?"


class FixSerialTransform(models.Model):
    """
    Helper model.
    Save object with old serial and new serial,  and serial key will be fixed in database.
    Serial keys can not be fixed directly.
    """
    old_serial = models.CharField(_("old serial"), max_length=32)
    new_serial = models.CharField(_("new serial"), max_length=32)
    category = models.ForeignKey("ItemCategory", verbose_name=_("item category"), on_delete=models.DO_NOTHING,
                                 blank=True, null=True)
    timestamp = models.DateTimeField(default=timezone.now)
    old_serial_obj = None

    class Meta:
        verbose_name = _("fix: serial transform")
        verbose_name_plural = _("fix: serial transforms")
        ordering = ['-timestamp']

    def __str__(self):
        return "%s -> %s" % (self.old_serial, self.new_serial)

    def clean_old_serial(self):
        try:
            self.old_serial_obj = ItemSerial.objects.get(serial=self.old_serial)
        except ItemSerial.DoesNotExist:
            raise ValidationError({'old_serial': "Serial number not found"})

    def clean_new_serial(self):
        try:
            serial = ItemSerial.objects.get(serial=self.new_serial)
        except ItemSerial.DoesNotExist:
            pass
        else:
            raise ValidationError({'new_serial': "Serial number already exists. "
                                                 "(%s, serial_id: %s, item_id: %s, category_id: %s, category_name: %s)" %
                                                 (serial.serial, serial.pk, serial.item_id,
                                                  serial.item.category_id, serial.item.category.name)
                                   })

    def clean(self):
        self.clean_old_serial()
        self.clean_new_serial()

    def rename_serial(self):
        assert self.old_serial_obj is not None, "Error! rename_serial called before clean_old_serial?"
        self.old_serial_obj.serial = self.new_serial
        self.old_serial_obj.save()
        self.category = self.old_serial_obj.item.category

    def save(self, *args, **kwargs):
        self.full_clean()
        self.rename_serial()
        super(FixSerialTransform, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        rev = FixSerialTransform(old_serial=self.new_serial, new_serial=self.old_serial)
        rev.save()


class FixCategoryMerge(models.Model):
    """
    Helper model.
    Save object with old ItemCategory and new ItemCategory. Items from the old ItemCategory will be moved
    to the new ItemCategory. All related data will be updated too. Old ItemCategory will be deleted.
     - data: logs in json format will be stored here.
     - old_category_sav_id: id of old category will be saved here.
     - old_category_sav_name: name of old category will be saved here.
    """
    old_category = models.ForeignKey("ItemCategory", verbose_name=_("old item category"),
                                     null=True, related_name="old_categoriess", on_delete=models.SET_NULL)
    new_category = models.ForeignKey("ItemCategory", verbose_name=_("new item category"),
                                     related_name="new_categoriess")
    old_category_sav_id = models.PositiveIntegerField(blank=True, null=True)
    old_category_sav_name = models.CharField(max_length=100, blank=True, null=True)
    timestamp = models.DateTimeField(default=timezone.now)
    data = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = _("fix: category merge")
        verbose_name_plural = _("fix: category merges")
        ordering = ['-timestamp']

    @staticmethod
    def get_related_models():
        """
        Setup which data will be altered and gathered for logging.
        PS: Ugly shit but it works.
        :return: list[list[model, *fields]]
        """
        return [
            [ItemCategoryComment, 'category_id', None, None, None],
            [Item, 'category_id', 'quantity', 'place_id', {'item': ['serials', 'chunks']}],
            [TransactionItem, 'category_id', None, None, None],
            [PurchaseItem, 'category_id', None, None, None],
            [FixSerialTransform, 'category_id', None, None, None],
            [FixCategoryMerge, 'old_category_id', None, None, None]
        ]

    def do_merge(self):
        """
        Don't touch this! Nobody knows how it works.

        Iterate via list of related models and alter data to merge contents of two item categories.
        :return:
        """
        data = {}
        # remove zero quantity items before merge
        Item.objects.filter(quantity=0, category=self.old_category).delete()
        Item.objects.filter(quantity=0, category=self.new_category).delete()
        """
        model - name of models which has relation with ItemCategory,
        field - name of field which points to ItemCategory,
        qf - quantity field - field which need to be summarized for two ItemCategories (actual only for Item)
        uniq - summarize qf field grouping by this field (Item.place_id)
        rel - reverse relation fields that need to be updated after summarization (ItemSerial, ItemChunk)
        """
        for model, field, qf, uniq, rel in self.get_related_models():
            q = {field: self.old_category_sav_id}
            u = {field: self.new_category_id}
            qs = model.objects.filter(**q)
            qs_list = copy(qs.values_list('id', flat=True))

            # store data for logging
            data.update({
                model.__name__: qs_list
            })

            # quantity field summarization
            if qf:

                for new_ins in qs:
                    # make filter for getting proper Item
                    # place_id and category_id are in `cu` filter
                    cu = copy(u)
                    cu.update({
                        uniq: getattr(new_ins, uniq)
                    })

                    try:
                        # try to get Item instance with new ItemCategory and specific place_id
                        old_ins = model.objects.get(**cu)
                    except model.DoesNotExist:
                        # no Item there: simply change category_id from old to new.
                        model.objects.filter(pk=new_ins.pk).update(**{field: self.new_category_id})
                    else:
                        # Item found there: update quantity of that item.
                        model.objects.filter(pk=old_ins.pk).update(**{qf: models.F(qf) + getattr(new_ins, qf)})
                        # And update item_id for all ItemSerial and ItemChunk related to destroyed item
                        for k in rel:
                            for r in rel[k]:
                                getattr(new_ins, r).all().update(**{k: old_ins})
                        # destroy item.
                        new_ins.delete()
            else:
                # if we don't need to fix quantity (all models except Item): simply update category_id value
                qs.update(**u)

        # save log data. We don't use self.data=data and self.save() to avoid merge infinite loop calling.
        self.__class__.objects.filter(pk=self.pk).update(data=str(data))
        c = self.old_category

        # delete old category.
        c.delete()

    def save(self, *args, **kwargs):
        if not self.old_category_sav_id:
            self.old_category_sav_id = self.old_category_id
            self.old_category_sav_name = self.old_category.name
        super(FixCategoryMerge, self).save(*args, **kwargs)
        if not self.data:
            self.do_merge()


class FixPlaceMerge(models.Model):
    """
    Helper model.
    Save object with old Place and new Place. Items from the old Place will be moved
    to the new Place. Old Place can be deleted safely after this process.
    See Place.join_to for details
    """
    old_place = models.ForeignKey("Place", related_name="old_places", verbose_name=_("old place"), null=True,
                                  on_delete=models.SET_NULL)
    new_place = models.ForeignKey("Place", related_name="new_places", verbose_name=_("new place"))
    old_place_sav_id = models.PositiveIntegerField(blank=True, null=True)
    old_place_sav_name = models.CharField(max_length=100, blank=True, null=True)
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = _("fix: place merge")
        verbose_name_plural = _("fix: place merges")
        ordering = ['-timestamp']

    def save(self, *args, **kwargs):
        if not self.old_place_sav_id and self.old_place:
            self.old_place_sav_id = self.old_place_id
            self.old_place_sav_name = self.old_place.name
            self.old_place.join_to(self.new_place)
        super(FixPlaceMerge, self).save(*args, **kwargs)


class Cell(models.Model):
    """
    Models for storing cells data
    """
    place = models.ForeignKey("Place", verbose_name=_("place"), related_name="cells")
    name = models.CharField(max_length=32)

    class Meta:
        verbose_name = _("cell")
        verbose_name_plural = _("cells")
        unique_together = ('place', 'name')

    def __str__(self):
        return self.name

    @staticmethod
    def autocomplete_search_fields():
        return "id__iexact", "name__icontains",


class TransmutationItem(MovementItem):
    """
    M2M Model for Transmutation and ItemCategory relations
    Transmutation.items = models.ManyToManyField("ItemCategory", through="TransmutationItem" ...)
    """
    transmuted = models.ForeignKey("ItemCategory", verbose_name=_("transmuted item category"),
                                   related_name="transmuted_categories")
    transmutation = models.ForeignKey("Transmutation", verbose_name=_("transmutation"),
                                      related_name="transmutation_items")
    ti = models.OneToOneField(TransactionItem, blank=True, null=True, related_name="transmutation_item")
    # Movement superclass
    # category = models.ForeignKey("ItemCategory", verbose_name=_("item category"))
    # quantity = models.DecimalField(_("quantity"), max_digits=9, decimal_places=3)
    # _chunks = models.TextField(blank=True, null=True)
    serial = models.ForeignKey(ItemSerial, blank=True, null=True, on_delete=models.SET_NULL)
    chunk = models.ForeignKey(ItemChunk, blank=True, null=True, on_delete=models.SET_NULL)
    cell = models.CharField(max_length=16, blank=True, null=True)

    class Meta:
        verbose_name = _("transmutation item")
        verbose_name_plural = _("transmutation items")

    def __str__(self):
        return "%s -> %s" % (self.category.name, self.transmuted.name)


class Transmutation(Transaction):
    # items = models.ManyToManyField("ItemCategory", through="TransmutationItem", verbose_name=_("items"),
    #                                through_fields=["transmutation", "category"])
    # source = models.ForeignKey("Place", verbose_name=_("source"), related_name="transmutation_sources")
    # destination = models.ForeignKey("Place", verbose_name=_("destination"), related_name="transmutation_destinations")
    # comment = models.TextField(_("comment"), blank=True, null=True)

    def save(self, *args, **kwargs):
        try:
            transmutator = Place.objects.get(pk=settings.APP_FILTERS['PLACE_TRANSMUTATOR_ID'])
        except Place.DoesNotExist:
            raise RuntimeError(_("Transmutator not found. Please check settings"))
        else:
            self.destination = transmutator
        super(Transmutation, self).save(*args, **kwargs)

    def force_complete(self, pending=False):
        self.is_negotiated_source = True
        self.is_negotiated_destination = True
        self.is_confirmed_source = True
        self.is_confirmed_destination = True
        self.complete(pending)

    @transaction.atomic
    def complete(self, pending=False, transmutation=True):
        """
        Same as Transaction.complete but prepared items will change_item category.
        :param pending:
        :param transmutation:
        :return:
        """
        if pending:
            # print "transaction complete defer"
            setattr(self, "is_pending", True)
            return

        if not self.is_prepared:
            self.prepare()
        self.check_prepared()

        for item in self.items_prepared:
            new_category = item.reserved_by.transmutation_item.transmuted
            item.category = new_category
            item.save()

        super(Transmutation, self).complete(pending=False, transmutation=True)

    def transmute(self):
        """
        Called from base.admin.TransmutationAdmin.save_formset
        Creates reversed transaction to return items with new categories from transmutator back to source Place
        :return:
        """
        if not self.transmutation_items.count():
            raise RuntimeError(ugettext("No transmutation items added"))
        # t = Transaction.objects.create(
        #     source = self.source,
        #     destination = self.destination,
        # )
        rev_t = Transaction.objects.create(
            destination=self.source,
            source=self.destination,
        )
        for tr in self.transmutation_items.all():
            ti = TransactionItem.objects.create(
                transaction=self.transaction_ptr,
                category=tr.category,
                quantity=tr.quantity,
                serial=tr.serial,
                chunk=tr.chunk,
                cell=tr.cell
            )
            tr.ti = ti
            tr.save()
            rev_ti = TransactionItem.objects.create(
                transaction=rev_t,
                category=tr.transmuted,
                quantity=tr.quantity,
                serial=tr.serial,
                cell=tr.cell
            )
        self.complete()
        rev_t.force_complete()

    class Meta:
        verbose_name = _("Fix: transmutation")
        verbose_name_plural = _("Fix: transmutations")


class Warranty(models.Model):
    """
    Warranty data for item serials.
    """
    serial = models.OneToOneField("ItemSerial", verbose_name=_("serial"))
    date = models.DateField(_("warranty date"))
    comment = models.TextField(_("comment"), blank=True, null=True)

    class Meta:
        verbose_name = _("warranty date")
        verbose_name_plural = _("warranty dates")

    def __str__(self):
        return self.serial.serial

    def category_name(self):
        return self.serial.item.category.name


class ReturnItem(MovementItem):
    """
    M2M Model for Return and ItemCategory relations
    Return.items = models.ManyToManyField("ItemCategory", through="ReturnItem" ...)
    """
    source = models.ForeignKey("Place", verbose_name=_("source"),
                               related_name="return_items", blank=True, null=True, on_delete=models.SET_NULL)
    ret = models.ForeignKey("Return", verbose_name=_("return"),
                            related_name="return_items")
    ti = models.OneToOneField(TransactionItem, blank=True, null=True, related_name="return_item")
    # Movement superclass
    # category = models.ForeignKey("ItemCategory", verbose_name=_("item category"))
    # quantity = models.DecimalField(_("quantity"), max_digits=9, decimal_places=3)
    # _chunks = models.TextField(blank=True, null=True)
    serial = models.CharField(max_length=32, blank=True, null=True)
    cell = models.CharField(max_length=16, blank=True, null=True)

    class Meta:
        verbose_name = _("return item")
        verbose_name_plural = _("return items")

    def __str__(self):
        return self.category.name


class Return(Transaction):
    """
    Model which creates one Purchase and two Transactions at once for each ReturnItem.
    Purchase: from Old Sklad `shop` to ReturnItem.destination
    Transaction: from ReturnItem.destination to Return.source
    Transaction: from Return.source to Return.destination

    One transaction can be omitted when ReturnItem.destination == Return.source. Not tested! Use carefully.
    Purchase can be omitted if ReturnItem.destination has Item available to withdraw.
    """
    @transaction.atomic
    def ret(self):
        """
        called from base.admin.ReturnAdmin.save_formset
        :return:
        """
        if not self.return_items.count():
            raise RuntimeError(ugettext("No return items added"))
        for ri in self.return_items.all():
            if ri.source and not ri.source == self.source:
                t_prep = Transaction.objects.create(
                    destination=self.source,
                    source=ri.source,
                )
                ti = None
                try:
                    if ri.serial:
                        serial = ItemSerial.objects.get(serial=ri.serial, item__category=ri.category)
                    else:
                        serial = None
                    ti = TransactionItem.objects.create(
                        transaction=t_prep,
                        category=ri.category,
                        quantity=ri.quantity,
                        serial=serial,
                        cell=ri.cell
                    )
                    ri.ti = ti
                    ri.save()
                    t_prep.force_complete()
                except (ItemNotFound, ItemSerial.DoesNotExist):
                    p_prep = Purchase.objects.create(
                        destination=ri.source,
                        source_id=settings.APP_FILTERS['PLACE_OLD_STORAGE'],
                        payer_id=settings.APP_FILTERS['PAYER_OLD_STORAGE'],
                        is_auto_source=True,
                        comment="Created automatically by return id:%s" % self.id
                    )
                    PurchaseItem.objects.create(
                        purchase=p_prep,
                        category=ri.category,
                        quantity=ri.quantity,
                        price=0,
                        _serials=ri.serial,
                        cell=ri.cell
                    )
                    p_prep.complete()
                    if ri.serial:
                        serial = ItemSerial.objects.get(
                            serial=ri.serial,
                            item__category=ri.category,
                            item__place=ri.source
                        )
                    else:
                        serial = None
                    if not ti:
                        ti = TransactionItem.objects.create(
                            transaction=t_prep,
                            category=ri.category,
                            quantity=ri.quantity,
                            serial=serial,
                            cell=ri.cell
                        )
                        ri.ti = ti
                        ri.save()
                    t_prep.force_complete()

            if ri.serial:
                serial = ItemSerial.objects.get(
                    serial=ri.serial,
                    item__category=ri.category,
                    item__place=self.source
                )
            else:
                serial = None

            TransactionItem.objects.create(
                transaction_id=self.transaction_ptr_id,
                category=ri.category,
                quantity=ri.quantity,
                serial=serial,
                cell=ri.cell
            )

        self.complete()
        self.transaction_ptr.created_at = timezone.now()
        self.transaction_ptr.save()

    class Meta:
        verbose_name = _("return")
        verbose_name_plural = _("returns")


class StorageToWorkerTransaction(Transaction):
    """
    Proxy model for WorkersAdmin
    """
    class Meta:
        proxy = True
        verbose_name = _("withdraw from storage")
        verbose_name_plural = _("withdraws from storage")


class WorkersItem(Item):
    """
    Proxy model for WorkersAdmin
    """
    class Meta:
        proxy = True
        verbose_name = _("worker's item")
        verbose_name_plural = _("worker's items")


class WorkersReturn(Return):
    """
    Proxy model for WorkersAdmin
    """
    class Meta:
        proxy = True
        verbose_name = _("worker's return from address")
        verbose_name_plural = _("worker's returns from addresses")


class WorkersUsed(Transaction):
    """
    Proxy model for WorkersAdmin
    """
    class Meta:
        proxy = True
        verbose_name = _("worker's used item")
        verbose_name_plural = _("worker's used items")


class WorkersInstalled(Transaction):
    """
    Proxy model for WorkersAdmin
    """
    class Meta:
        proxy = True
        verbose_name = _("worker's installed item")
        verbose_name_plural = _("worker's installed items")
