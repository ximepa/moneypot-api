# coding=utf-8

from functools import update_wrapper

from django.contrib import admin
from django import forms
from django_mptt_admin.admin import DjangoMpttAdmin
from django.utils.translation import ugettext_lazy as _, ugettext
from django.utils.html import mark_safe
from django.core.urlresolvers import reverse
from django.conf.urls import url
from django.db.models import Q
from daterange_filter.filter import DateRangeFilter

from actions import process_to_void
from overrides import AdminReadOnly, InlineReadOnly, HiddenAdminModelMixin
from functions import create_model_admin
from forms import ItemCategoryForm, PlaceForm, PurchaseItemForm, TransactionItemForm, PurchaseForm, TransactionForm
from inlines import ItemCategoryCommentInline, PurchaseItemInline, PurchaseItemInlineReadonly, \
    TransactionItemInlineReadonly, TransactionItemInline, TransactionCommentPlaceInline
from base.models import Unit, ItemCategory, Place, PurchaseItem, Payer, Purchase, Item, ItemSerial, ItemChunk, \
    TransactionItem, Transaction, OrderItemSerial, ContractItemSerial, VItemMovement, VSerialMovement, get_descendants_ids


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    pass


@admin.register(ItemCategory)
class ItemCategoryAdmin(DjangoMpttAdmin):
    form = ItemCategoryForm
    search_fields = ['name', ]
    tree_auto_open = False
    inlines = [ItemCategoryCommentInline]


@admin.register(Place)
class PlaceAdmin(DjangoMpttAdmin):
    search_fields = ['name', ]
    tree_auto_open = False
    form = PlaceForm
    list_display = ['__unicode__', 'is_shop', 'items_changelist_link']

    def items_changelist_link(self, obj):
        link = reverse("admin:base_place_item_changelist", args=[obj.id])
        return mark_safe(u'<a href="%s">%s</a>' % (link, _("items list")))


@admin.register(PurchaseItem)
class PurchaseItemAdmin(HiddenAdminModelMixin, AdminReadOnly):
    pass


@admin.register(Payer)
class PayerAdmin(admin.ModelAdmin):
    search_fields = ['name', ]


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    form = PurchaseForm
    inlines = [PurchaseItemInline, ]
    list_display = ['__unicode__', 'created_at', 'completed_at', 'source', 'destination', 'is_completed',
                    'is_prepared', ]
    list_filter = ['source', 'destination', 'is_completed', 'is_prepared', ]
    search_fields = ['source__name', 'destination__name', 'purchase_items__category__name']

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(self.readonly_fields)
        if obj and obj.is_completed:
            readonly_fields.extend(['source', 'destination', 'completed_at', 'is_auto_source'])
            dir(self.form)
        return readonly_fields

    def get_fields(self, request, obj=None):
        fields = super(PurchaseAdmin, self).get_fields(request, obj)
        if obj and obj.is_completed:
            fields.remove('force_complete')
        return fields

    def get_inline_instances(self, request, obj=None):
        inline_instances = []

        if obj and obj.is_completed:
            inlines = [PurchaseItemInlineReadonly, ]
        else:
            inlines = self.inlines

        for inline_class in inlines:
            inline = inline_class(self.model, self.admin_site)
            inline_instances.append(inline)
        return inline_instances

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if formset.form.__name__ == PurchaseItemForm.__name__ and instance.purchase.is_completed:
                raise forms.ValidationError(ugettext("purchase items data is read only!"))
            instance.save()
        formset.save_m2m()


@admin.register(Item)
class ItemAdmin(AdminReadOnly):
    search_fields = ['category__name', 'place__name']
    list_filter = ['category', ]
    list_display = ['__unicode__', 'quantity', 'place']


@admin.register(ItemSerial)
class ItemSerialAdmin(AdminReadOnly):

    def get_queryset(self, request):
        return super(ItemSerialAdmin, self).get_queryset(request).select_related('item', 'item__category', 'item__place')

    def owner(self, instance):
        return instance.item.place.name

    def serial_movement_changelist_link(self, obj):
        link = reverse("admin:base_serial_movement_filtered_changelist", args=[obj.id])
        return mark_safe(u'<a href="%s">%s</a>' % (link, _("movement history")))

    search_fields = ['item__category__name', 'serial']
    list_filter = ['item__category', ]
    list_display = ['__unicode__', 'category_name', 'owner', 'serial_movement_changelist_link']


@admin.register(ItemChunk)
class ItemChunkAdmin(HiddenAdminModelMixin, AdminReadOnly):
    search_fields = ['item__category__name']
    list_filter = ['item__category', ]
    list_display = ['__unicode__', 'category_name']


@admin.register(TransactionItem)
class TransactionItemAdmin(HiddenAdminModelMixin, AdminReadOnly):
    pass


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    class Media:
        js = ('base/js/transaction_source_item_autocomplete.js',)

    form = TransactionForm
    list_display = ['__unicode__', 'created_at', 'completed_at', 'source', 'destination', 'is_completed', 'is_prepared',
                    'is_negotiated_source', 'is_negotiated_destination', 'is_confirmed_source',
                    'is_confirmed_destination']
    list_filter = ['source', 'destination', 'is_completed', 'is_prepared',
                   'is_negotiated_source', 'is_negotiated_destination', 'is_confirmed_source',
                   'is_confirmed_destination']
    search_fields = ['source__name', 'destination__name', 'transaction_items__category__name']
    inlines = [
        TransactionItemInline, TransactionCommentPlaceInline
    ]

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(self.readonly_fields)
        if obj and obj.is_completed:
            readonly_fields.extend(['source', 'destination', 'completed_at'])
        return readonly_fields

    def get_fields(self, request, obj=None):
        fields = super(TransactionAdmin, self).get_fields(request, obj)
        if obj and obj.is_completed:
            fields.remove('force_complete')
        return fields

    def get_inline_instances(self, request, obj=None):
        inline_instances = []

        if obj and obj.is_completed:
            inlines = [TransactionItemInlineReadonly, ]
        else:
            inlines = self.inlines

        for inline_class in inlines:
            inline = inline_class(self.model, self.admin_site)
            inline_instances.append(inline)
        return inline_instances

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if formset.form.__name__ == TransactionItemForm.__name__ and instance.transaction.is_completed:
                raise forms.ValidationError(ugettext("transaction items data is read only!"))
            instance.save()
        formset.save_m2m()


class PlaceItemAdmin(HiddenAdminModelMixin, ItemAdmin):
    place_id = None
    list_display = ['obj_link', 'quantity', 'place', 'items_serials_changelist_link',
                    'items_chunks_changelist_link', 'item_movement_changelist_link']

    def obj_link(self, obj):
        # link = reverse("admin:base_item_change", args=[obj.id])
        link = reverse("admin:base_place_item_change", args=[self.place_id, obj.id])
        return mark_safe(u'<a href="%s">%s</a>' % (link, obj.__unicode__()))

    def items_serials_changelist_link(self, obj):
        link = reverse("admin:base_item_serials_filtered_changelist", args=[obj.id])
        return mark_safe(u'<a href="%s">%s</a>' % (link, _("serials list")))

    def items_chunks_changelist_link(self, obj):
        # link = reverse("admin:base_item_serials_filtered_changelist", args=[obj.id])
        link = "#%s" % obj.id
        return mark_safe(u'<a href="%s">%s</a>' % (link, _("chunks list")))

    def item_movement_changelist_link(self, obj):
        link = reverse("admin:base_item_movement_filtered_changelist", args=[self.place_id, obj.category_id])
        return mark_safe(u'<a href="%s">%s</a>' % (link, _("movement history")))

    def get_queryset(self, request):
        qs = super(PlaceItemAdmin, self).get_queryset(request)
        return qs.filter(place_id=self.place_id)

    def changelist_view(self, request, place_id, extra_context=None):  # pylint:disable=arguments-differ
        self.place_id = place_id
        extra_context = extra_context or {}
        try:
            place = Place.objects.get(pk=place_id)
        except Place.DoesNotExist:
            extra_context.update({'cl_header': _('Place does not exist')})
        else:
            extra_context.update({'cl_header': _(u"Items for <{name}>".format(name=unicode(place.name)))})
        view = super(PlaceItemAdmin, self).changelist_view(request, extra_context=extra_context)
        return view

    def change_view(self, request, place_id, object_id, form_url='',
                    extra_context=None):  # pylint:disable=arguments-differ
        self.place_id = place_id
        extra_context = extra_context or {}
        extra_context.update({
            'place_id': place_id,
            'proxy_url': "admin:base_place_item_changelist",
            'proxy_url_arg': self.place_id,
        })
        try:
            item = Item.objects.get(pk=object_id)
        except Item.DoesNotExist:
            extra_context.update({'obj_header': _('Serial does not exist')})
        else:
            extra_context.update({'obj_header': unicode(item.category.name)})
        try:
            place = Place.objects.get(pk=place_id)
        except Place.DoesNotExist:
            extra_context.update({'cl_header': _('Place does not exist')})
        else:
            extra_context.update({'cl_header': _(u"Items for <{name}>".format(name=unicode(place.name)))})
        return super(PlaceItemAdmin, self).change_view(request, object_id, form_url='', extra_context=extra_context)

    def get_urls(self):

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)

            return update_wrapper(wrapper, view)

        urlpatterns = [
            url(r'^(\d+)/$', wrap(self.changelist_view), name='base_place_item_changelist'),
            url(r'^(\d+)/(\d+)$', wrap(self.change_view), name='base_place_item_change'),
        ]
        return urlpatterns

    change_list_template = 'admin/proxy_change_list.html'
    change_form_template = 'admin/proxy_change_form.html'


create_model_admin(PlaceItemAdmin, name='place_item', model=Item)


class ItemSerialsFilteredAdmin(HiddenAdminModelMixin, ItemSerialAdmin):
    item_id = None
    list_display = ['obj_link', 'category_name', 'serial_movement_changelist_link']

    def obj_link(self, obj):
        link = reverse("admin:base_item_serials_filtered_change", args=[self.item_id, obj.id])
        return mark_safe(u'<a href="%s">%s</a>' % (link, obj.__unicode__()))

    def serial_movement_changelist_link(self, obj):
        link = reverse("admin:base_serial_movement_filtered_changelist", args=[obj.id])
        return mark_safe(u'<a href="%s">%s</a>' % (link, _("movement history")))

    def get_queryset(self, request):
        qs = super(ItemSerialsFilteredAdmin, self).get_queryset(request)
        return qs.filter(item_id=self.item_id)

    def changelist_view(self, request, item_id, extra_context=None):  # pylint:disable=arguments-differ
        self.item_id = item_id
        extra_context = extra_context or {}
        try:
            item = Item.objects.get(pk=item_id)
        except Item.DoesNotExist:
            extra_context.update({'cl_header': _('Item does not exist')})
        else:
            extra_context.update({'cl_header': _(u"Serials for <{name}> in <{place}>".format(
                name=unicode(item.category.name),
                place=unicode(item.place.name)
            ))})
        view = super(ItemSerialsFilteredAdmin, self).changelist_view(request, extra_context=extra_context)
        return view

    def change_view(self, request, item_id, object_id, form_url='',
                    extra_context=None):  # pylint:disable=arguments-differ
        self.item_id = item_id
        extra_context = extra_context or {}
        extra_context.update({
            'item_id': item_id,
            'proxy_url': "admin:base_item_serials_filtered_changelist",
            'proxy_url_arg': self.item_id,
        })
        try:
            serial = ItemSerial.objects.get(pk=object_id)
        except ItemSerial.DoesNotExist:
            extra_context.update({'obj_header': _('Serial does not exist')})
        else:
            extra_context.update({'obj_header': unicode(serial.serial)})
        try:
            item = Item.objects.get(pk=item_id)
        except Item.DoesNotExist:
            extra_context.update({'cl_header': _('Item does not exist')})
        else:
            extra_context.update({'cl_header': _(u"Serials for <{name}> in <{place}>".format(
                name=unicode(item.category.name),
                place=unicode(item.place.name)
            ))})
        return super(ItemSerialsFilteredAdmin, self).change_view(request, object_id, form_url='',
                                                                 extra_context=extra_context)

    def get_urls(self):

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)

            return update_wrapper(wrapper, view)

        urlpatterns = [
            url(r'^(\d+)/$', wrap(self.changelist_view), name='base_item_serials_filtered_changelist'),
            url(r'^(\d+)/(\d+)$', wrap(self.change_view), name='base_item_serials_filtered_change'),
        ]
        return urlpatterns

    change_list_template = 'admin/proxy_change_list.html'
    change_form_template = 'admin/proxy_change_form.html'


create_model_admin(ItemSerialsFilteredAdmin, name='item_serials_filtered', model=ItemSerial)


@admin.register(OrderItemSerial)
class OrderItemSerialAdmin(admin.ModelAdmin):
    search_fields = ['serial']
    # list_filter = ['item__place', ]
    list_display = ['serial', 'category_name', 'owner', 'comment']
    ordering = ['comment', ]
    readonly_fields = ['item', 'purchase', 'serial', 'owner']
    fields = ['comment', 'serial', 'owner']
    actions = [process_to_void]

    def get_queryset(self, request):
        qs = super(OrderItemSerialAdmin, self).get_queryset(request).select_related(
            'item', 'item__category', 'item__place'
        )
        return qs.filter(
            item__category_id__in=get_descendants_ids(ItemCategory, 89),
            item__place_id__in=get_descendants_ids(Place, 14)
        )

    def owner(self, instance):
        return instance.item.place.name


@admin.register(ContractItemSerial)
class ContractItemSerialAdmin(admin.ModelAdmin):
    search_fields = ['serial']
    list_filter = ['item__place', ]
    list_display = ['serial', 'category_name', 'owner', 'comment']
    ordering = ['comment', ]
    readonly_fields = ['item', 'purchase', 'serial', 'owner']
    fields = ['comment', 'serial', 'owner']
    actions = [process_to_void]

    def get_queryset(self, request):
        qs = super(ContractItemSerialAdmin, self).get_queryset(request).select_related(
            'item', 'item__category', 'item__place'
        )
        return qs.filter(
            item__category_id__in=get_descendants_ids(ItemCategory, 88),
            item__place_id__in=get_descendants_ids(Place, 14)
        )

    def owner(self, instance):
        return instance.item.place.name



@admin.register(VItemMovement)
class ItemMovementAdmin(AdminReadOnly):
    search_fields = ['destination_name', 'source_name', 'item_category_name']
    list_filter = (
        ('created_at', DateRangeFilter),
        ('completed_at', DateRangeFilter),
        'category',
    )
    list_display = ['item_category_name', 'created_at', 'completed_at', 'source', 'destination', 'quantity']
    fields = ['item_category_name', 'created_at', 'completed_at', 'source', 'destination', 'quantity']


@admin.register(VSerialMovement)
class SerialMovementAdmin(AdminReadOnly):
    search_fields = ['destination_name', 'source_name', 'item_category_name', 'serial']
    list_filter = (
        ('created_at', DateRangeFilter),
        ('completed_at', DateRangeFilter),
        'category',
    )
    list_display = ['serial', 'item_category_name', 'created_at', 'completed_at', 'source', 'destination', 'quantity']
    fields = ['serial', 'item_category_name', 'created_at', 'completed_at', 'source', 'destination', 'quantity']


class ItemMovementFilteredAdmin(HiddenAdminModelMixin, ItemMovementAdmin):
    place_id = None
    category_id = None

    def get_queryset(self, request):
        qs = super(ItemMovementFilteredAdmin, self).get_queryset(request)
        qs = qs.filter(Q(source_id=self.place_id) | Q(destination_id=self.place_id))
        if self.category_id:
            qs = qs.filter(category_id=self.category_id)
        return qs

    def changelist_view(self, request, place_id, category_id=None, extra_context=None):  # pylint:disable=arguments-differ
        self.place_id = place_id
        self.category_id = category_id
        extra_context = extra_context or {}
        try:
            place = Place.objects.get(pk=place_id)
        except Place.DoesNotExist:
            place_name = "unknown place"
        else:
            place_name = place.name
        if category_id:
            try:
                category = ItemCategory.objects.get(pk=category_id)
            except ItemCategory.DoesNotExist:
                category_name = "unknown category"
            else:
                category_name = category.name
            extra_context.update({'cl_header': _(u"Movement history for <{category_name}> in <{place_name}>".format(
                    category_name=unicode(category_name),
                    place_name=unicode(place_name)
                ))})
        else:
            extra_context.update({'cl_header': _(u"Movement history for <{place_name}>".format(
                    place_name=unicode(place_name)
                ))})
        view = super(ItemMovementFilteredAdmin, self).changelist_view(request, extra_context=extra_context)
        return view

    def get_urls(self):

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)

            return update_wrapper(wrapper, view)

        urlpatterns = [
            url(r'^(\d+)/(\d+)/$', wrap(self.changelist_view), name='base_item_movement_filtered_changelist'),
            url(r'^(\d+)/$', wrap(self.changelist_view), name='base_item_movement_filtered_changelist'),
        ]
        return urlpatterns

    change_list_template = 'admin/proxy_change_list.html'

create_model_admin(ItemMovementFilteredAdmin, name='item_movement_filtered', model=VItemMovement)


class SerialMovementFilteredAdmin(HiddenAdminModelMixin, SerialMovementAdmin):
    place_id = None
    serial_id = None

    def get_queryset(self, request):
        qs = super(SerialMovementFilteredAdmin, self).get_queryset(request)
        qs = qs.filter(serial_id=self.serial_id)
        if self.place_id:
            qs = qs.filter(Q(source_id=self.place_id) | Q(destination_id=self.place_id))
        return qs

    def changelist_view(self, request, serial_id, place_id=None,  extra_context=None):  # pylint:disable=arguments-differ
        self.place_id = place_id
        self.serial_id = serial_id
        extra_context = extra_context or {}
        try:
            serial = ItemSerial.objects.get(pk=serial_id)
        except ItemCategory.DoesNotExist:
            serial_name = "unknown serial"
        else:
            serial_name = serial.serial
        if place_id:
            try:
                place = Place.objects.get(pk=place_id)
            except Place.DoesNotExist:
                place_name = "unknown place"
            else:
                place_name = place.name
            extra_context.update({'cl_header': _(u"Movement history for <{serial_name}> in <{place_name}>".format(
                    serial_name=unicode(serial_name),
                    place_name=unicode(place_name)
                ))})
        else:
            extra_context.update({'cl_header': _(u"Movement history for <{serial_name}>".format(
                    serial_name=unicode(serial_name),
                ))})
        view = super(SerialMovementFilteredAdmin, self).changelist_view(request, extra_context=extra_context)
        return view

    def get_urls(self):

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)

            return update_wrapper(wrapper, view)

        urlpatterns = [
            url(r'^(\d+)/(\d+)/$', wrap(self.changelist_view), name='base_serial_movement_filtered_changelist'),
            url(r'^(\d+)/$', wrap(self.changelist_view), name='base_serial_movement_filtered_changelist'),
        ]
        return urlpatterns

    change_list_template = 'admin/proxy_change_list.html'

create_model_admin(SerialMovementFilteredAdmin, name='serial_movement_filtered', model=VSerialMovement)