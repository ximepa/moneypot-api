# coding=utf-8

from functools import update_wrapper

from django.contrib import admin
from django import forms
from django.core.exceptions import ValidationError
from django_mptt_admin.admin import DjangoMpttAdmin
from django.utils.translation import ugettext_lazy as _, ugettext
from django.utils.html import mark_safe
from django.core.urlresolvers import reverse
from django.conf.urls import url
from django.contrib.admin.utils import quote
from django.contrib import messages
from django.db.models import Q
from django.db import models
from daterange_filter.filter import DateRangeFilter
from django_mptt_admin import util
from grappelli_filters import RelatedAutocompleteFilter, FiltersMixin

from actions import process_to_void
from overrides import AdminReadOnly, InlineReadOnly, HiddenAdminModelMixin
from functions import create_model_admin
from forms import ItemCategoryForm, PlaceForm, PurchaseItemForm, TransactionItemForm, PurchaseForm, TransactionForm, \
    FixCategoryMergeForm, CellForm, CellItemForm, CellItemActionForm
from inlines import ItemCategoryCommentInline, PurchaseItemInline, PurchaseItemInlineReadonly, \
    TransactionItemInlineReadonly, TransactionItemInline, TransactionCommentPlaceInline
from base.models import Unit, ItemCategory, Place, PurchaseItem, Payer, Purchase, Item, ItemSerial, ItemChunk, \
    TransactionItem, Transaction, OrderItemSerial, ContractItemSerial, VItemMovement, VSerialMovement, \
    get_descendants_ids, FixSerialTransform, FixCategoryMerge, Cell, CellItem
from filebrowser.widgets import ClearableFileInput
from filebrowser.settings import ADMIN_THUMBNAIL


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    pass


@admin.register(ItemCategory)
class ItemCategoryAdmin(DjangoMpttAdmin):

    class Media:
        js = ('base/js/category_parent_autocomplete.js',)

    change_tree_template = u'admin/mptt_change_list.html'
    form = ItemCategoryForm
    search_fields = ['name', ]
    tree_auto_open = False
    inlines = [ItemCategoryCommentInline]
    list_display = ['name', 'image_thumbnail']

    def image_thumbnail(self, obj):
        if obj.photo:
            if obj.photo.filetype == "Image":
                return '<a href="%s"><img src="%s" /></a>' % (obj.photo.url, obj.photo.version_generate(ADMIN_THUMBNAIL).url)
            else:
                return '<a href="%s">%s</a>' % (obj.photo.url, obj.photo.url)
        else:
            return ""
    image_thumbnail.allow_tags = True
    image_thumbnail.short_description = "Thumbnail"

    def get_tree_data(self, qs, max_level):
        pk_attname = self.model._meta.pk.attname

        def handle_create_node(instance, node_info):
            pk = quote(getattr(instance, pk_attname))

            if Item.objects.filter(category_id=pk).count():
                node_info.update(
                    view_url=reverse("admin:base_category_item_changelist", args=[pk]),
                    transfer_url=reverse("admin:base_item_movement_filtered_changelist", args=[0, pk]),
                )
            node_info.update(
                url=self.get_admin_url('change', (quote(pk),)),
                move_url=self.get_admin_url('move', (quote(pk),))
            )

        return util.get_tree_from_queryset(qs, handle_create_node, max_level)


@admin.register(Place)
class PlaceAdmin(DjangoMpttAdmin):
    change_tree_template = u'admin/mptt_change_list.html'
    search_fields = ['name', ]
    tree_auto_open = False
    form = PlaceForm
    list_display = ['__unicode__', 'is_shop', 'items_changelist_link']

    def items_changelist_link(self, obj):
        link = reverse("admin:base_place_item_changelist", args=[obj.id])
        return mark_safe(u'<a href="%s">%s</a>' % (link, _("items list")))

    def get_tree_data(self, qs, max_level):
        pk_attname = self.model._meta.pk.attname

        def handle_create_node(instance, node_info):
            pk = quote(getattr(instance, pk_attname))

            if Item.objects.filter(place_id=pk).count():
                node_info.update(
                    view_url=reverse("admin:base_place_item_changelist", args=[pk]),
                    transfer_url=reverse("admin:base_item_movement_filtered_changelist", args=[pk]),
                )
            node_info.update(
                url=self.get_admin_url('change', (quote(pk),)),
                move_url=self.get_admin_url('move', (quote(pk),))
            )

        return util.get_tree_from_queryset(qs, handle_create_node, max_level)



@admin.register(PurchaseItem)
class PurchaseItemAdmin(HiddenAdminModelMixin, AdminReadOnly):
    pass


@admin.register(Payer)
class PayerAdmin(admin.ModelAdmin):
    search_fields = ['name', ]


@admin.register(Purchase)
class PurchaseAdmin(FiltersMixin, admin.ModelAdmin):
    class Media:
        js = ('base/js/purchase_source_item_autocomplete.js',)

    form = PurchaseForm
    inlines = [PurchaseItemInline, ]
    list_display = ['__unicode__', 'created_at', 'completed_at', 'source', 'destination', 'is_completed',
                    'is_prepared', ]
    list_filter = [
        ('source', RelatedAutocompleteFilter),
        ('destination', RelatedAutocompleteFilter),
        'is_completed', 'is_prepared',
    ]
    search_fields = ['source__name', 'destination__name', 'purchase_items__category__name']

    def has_delete_permission(self, request, obj=None):
        if obj and obj.is_completed:
            return False
        else:
            return super(PurchaseAdmin, self).has_delete_permission(request, obj)

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
        for obj in formset.deleted_objects:
            obj.delete()
        for instance in instances:
            if formset.form.__name__ == PurchaseItemForm.__name__ and instance.purchase.is_completed:
                raise ValidationError(ugettext("purchase items data is read only!"))
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
class TransactionAdmin(FiltersMixin, admin.ModelAdmin):
    class Media:
        js = ('base/js/transaction_source_item_autocomplete.js',)

    form = TransactionForm
    list_display = [
        '__unicode__', 'created_at', 'completed_at',
        'source', 'destination', 'is_completed', 'is_prepared',
        # 'is_negotiated_source', 'is_negotiated_destination', 'is_confirmed_source',
        # 'is_confirmed_destination'
    ]
    list_filter = [
        ('source', RelatedAutocompleteFilter),
        ('destination', RelatedAutocompleteFilter),
        'is_completed', 'is_prepared',
        # 'is_negotiated_source', 'is_negotiated_destination', 'is_confirmed_source',
        # 'is_confirmed_destination'
    ]
    search_fields = ['source__name', 'destination__name', 'transaction_items__category__name']
    inlines = [
        TransactionItemInline, TransactionCommentPlaceInline
    ]

    def has_delete_permission(self, request, obj=None):
        if obj and obj.is_completed:
            return False
        else:
            return super(TransactionAdmin, self).has_delete_permission(request, obj)

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
        print change
        instances = formset.save(commit=False)
        for obj in formset.deleted_objects:
            obj.delete()
        for instance in instances:
            if formset.form.__name__ == TransactionItemForm.__name__ and instance.transaction.is_completed:
                err = 1
                for ti in instance.transaction.transaction_items.all():
                    if ti.pk == instance.pk:
                        err = 0
                if err:
                    raise ValidationError(ugettext("transaction items data is read only!"))
            else:
                trash = getattr(instance, "trash", False)
                if not trash:
                    instance.save()
                elif instance.pk:
                    instance.delete()
        formset.save_m2m()

    def rollback(self, request, queryset):
        for t in queryset:
            if not t.is_completed:
                self.message_user(request,
                                  _("Transaction {trans} not completed. cannot rollback".format(trans=t)),
                                  level=messages.ERROR)
            else:
                for ti in t.transaction_items.all():
                    t = Transaction.objects.create(source=ti.destination, destination=ti.transaction.source)
                    ti.pk = None
                    ti.transaction = t
                    ti.destination = None
                    ti.save()
                    t.force_complete()

    rollback.short_description = _('rollback')

    actions = [rollback]


class PlaceItemAdmin(HiddenAdminModelMixin, ItemAdmin):
    place_id = None
    show_zero = None
    list_display = ['__unicode__', 'quantity', 'place', 'cell', 'items_serials_changelist_link',
                    # 'items_chunks_changelist_link',
                    'item_movement_changelist_link']

    # def obj_link(self, obj):
    #     # link = reverse("admin:base_item_change", args=[obj.id])
    #     # link = reverse("admin:base_place_item_change", args=[self.place_id, obj.id])
    #     link="#"
    #     return mark_safe(u'<a href="%s">%s</a>' % (link, obj.__unicode__()))

    def items_serials_changelist_link(self, obj):
        link = reverse("admin:base_item_serials_filtered_changelist", args=[obj.id])
        return mark_safe(u'<a href="%s">%s</a>' % (link, _("serials list")))

    items_serials_changelist_link.short_description = _("serials")

    def items_chunks_changelist_link(self, obj):
        # link = reverse("admin:base_item_serials_filtered_changelist", args=[obj.id])
        link = "#%s" % obj.id
        return mark_safe(u'<a href="%s">%s</a>' % (link, _("chunks list")))

    items_chunks_changelist_link.short_description = _("chunks")

    def item_movement_changelist_link(self, obj):
        link = reverse("admin:base_item_movement_filtered_changelist", args=[self.place_id, obj.category_id])
        return mark_safe(u'<a href="%s">%s</a>' % (link, _("movement history")))

    item_movement_changelist_link.short_description = _("movement history")

    def cell(self, obj):
        if not obj.place.has_cells:
            return ""
        l = obj.category.cell_items.filter(place=obj.place, cell_isnull=False).values_list("cell__name", flat=True)
        return "/".join(sorted(list(set(l))))

    def get_queryset(self, request):
        qs = super(PlaceItemAdmin, self).get_queryset(request)
        qs = qs.filter(place_id=self.place_id)
        if not self.show_zero:
            qs = qs.filter(quantity__gt=0)
        return qs

    def changelist_view(self, request, place_id, extra_context=None):  # pylint:disable=arguments-differ
        request.GET._mutable = True
        self.show_zero = int(request.GET.pop("show_zero", ["0"])[0])
        request.GET.pop("a", None)
        rq_qs = "?" + (request.GET.urlencode() or "a=1")
        self.place_id = place_id
        extra_context = extra_context or {}
        try:
            place = Place.objects.get(pk=place_id)
        except Place.DoesNotExist:
            extra_context.update({'cl_header': _('Place does not exist')})
        else:
            cl_header = _(u"Items for <{name}>".format(name=unicode(place.name)))
            extra_context.update({'show_zero': self.show_zero})
            extra_context.update({'rq_qs': rq_qs})
            extra_context.update({'cl_header': mark_safe(cl_header)})
        view = super(PlaceItemAdmin, self).changelist_view(request, extra_context=extra_context)
        return view

    # def change_view(self, request, place_id, object_id, form_url='',
    #                 extra_context=None):  # pylint:disable=arguments-differ
    #     self.place_id = place_id
    #     extra_context = extra_context or {}
    #     extra_context.update({
    #         'place_id': place_id,
    #         'proxy_url': "admin:base_place_item_changelist",
    #         'proxy_url_arg': self.place_id,
    #     })
    #     try:
    #         item = Item.objects.get(pk=object_id)
    #     except Item.DoesNotExist:
    #         extra_context.update({'obj_header': _('Serial does not exist')})
    #     else:
    #         extra_context.update({'obj_header': unicode(item.category.name)})
    #     try:
    #         place = Place.objects.get(pk=place_id)
    #     except Place.DoesNotExist:
    #         extra_context.update({'cl_header': _('Place does not exist')})
    #     else:
    #         cl_header = _(u"Items for <{name}>".format(name=unicode(place.name)))
    #         extra_context.update({'cl_header': cl_header})
    #     return super(PlaceItemAdmin, self).change_view(request, object_id, form_url='', extra_context=extra_context)

    def get_urls(self):

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)

            return update_wrapper(wrapper, view)

        urlpatterns = [
            url(r'^(\d+)/$', wrap(self.changelist_view), name='base_place_item_changelist'),
            # url(r'^(\d+)/(\d+)$', wrap(self.change_view), name='base_place_item_change'),
        ]
        return urlpatterns

    change_list_template = 'admin/proxy_change_list.html'
    change_form_template = 'admin/proxy_change_form.html'


create_model_admin(PlaceItemAdmin, name='place_item', model=Item)


class CategoryItemAdmin(HiddenAdminModelMixin, ItemAdmin):
    category_id = None
    show_zero = None
    list_display = ['__unicode__', 'quantity', 'place', 'items_serials_changelist_link',
                    'items_chunks_changelist_link', 'item_movement_changelist_link']

    def items_serials_changelist_link(self, obj):
        link = reverse("admin:base_item_serials_filtered_changelist", args=[obj.id])
        return mark_safe(u'<a href="%s">%s</a>' % (link, _("serials list")))

    def items_chunks_changelist_link(self, obj):
        link = "#%s" % obj.id
        return mark_safe(u'<a href="%s">%s</a>' % (link, _("chunks list")))

    def item_movement_changelist_link(self, obj):
        link = reverse("admin:base_item_movement_filtered_changelist", args=[0, obj.category_id])
        return mark_safe(u'<a href="%s">%s</a>' % (link, _("movement history")))

    def get_queryset(self, request):
        qs = super(CategoryItemAdmin, self).get_queryset(request)
        qs = qs.filter(category_id=self.category_id)
        if not self.show_zero:
            qs = qs.filter(quantity__gt=0)
        return qs

    def changelist_view(self, request, category_id, extra_context=None):  # pylint:disable=arguments-differ
        request.GET._mutable = True
        self.show_zero = int(request.GET.pop("show_zero", ["0"])[0])
        request.GET.pop("a", None)
        rq_qs = "?" + (request.GET.urlencode() or "a=1")
        self.category_id = category_id
        extra_context = extra_context or {}
        try:
            category = ItemCategory.objects.get(pk=category_id)
        except ItemCategory.DoesNotExist:
            extra_context.update({'cl_header': _('Category does not exist')})
        else:
            cl_header = _(u"<{name}> items".format(name=unicode(category.name)))
            extra_context.update({'show_zero': self.show_zero})
            extra_context.update({'rq_qs': rq_qs})
            extra_context.update({'cl_header': mark_safe(cl_header)})
        view = super(CategoryItemAdmin, self).changelist_view(request, extra_context=extra_context)
        return view

    def get_urls(self):

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)

            return update_wrapper(wrapper, view)

        urlpatterns = [
            url(r'^(\d+)/$', wrap(self.changelist_view), name='base_category_item_changelist'),
        ]
        return urlpatterns

    change_list_template = 'admin/proxy_change_list.html'
    change_form_template = 'admin/proxy_change_form.html'


create_model_admin(CategoryItemAdmin, name='category_item', model=Item)


class ItemSerialsFilteredAdmin(HiddenAdminModelMixin, ItemSerialAdmin):
    item_id = None
    list_display = ['__unicode__', 'category_name', 'cell', 'serial_movement_changelist_link']

    # def obj_link(self, obj):
    #     link = reverse("admin:base_item_serials_filtered_change", args=[self.item_id, obj.id])
    #     return mark_safe(u'<a href="%s">%s</a>' % (link, obj.__unicode__()))

    def serial_movement_changelist_link(self, obj):
        link = reverse("admin:base_serial_movement_filtered_changelist", args=[obj.id])
        return mark_safe(u'<a href="%s">%s</a>' % (link, _("movement history")))

    serial_movement_changelist_link.short_description = _("movement history")

    def cell(self, obj):
        if not obj.item.place.has_cells:
            return ""
        l = obj.item.category.cell_items.filter(
            place=obj.item.place,
            serial=obj,
            cell_isnull=False).values_list("cell__name", flat=True)
        return "/".join(sorted(list(set(l))))

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

    # def change_view(self, request, item_id, object_id, form_url='',
    #                 extra_context=None):  # pylint:disable=arguments-differ
    #     self.item_id = item_id
    #     extra_context = extra_context or {}
    #     extra_context.update({
    #         'item_id': item_id,
    #         'proxy_url': "admin:base_item_serials_filtered_changelist",
    #         'proxy_url_arg': self.item_id,
    #     })
    #     try:
    #         serial = ItemSerial.objects.get(pk=object_id)
    #     except ItemSerial.DoesNotExist:
    #         extra_context.update({'obj_header': _('Serial does not exist')})
    #     else:
    #         extra_context.update({'obj_header': unicode(serial.serial)})
    #     try:
    #         item = Item.objects.get(pk=item_id)
    #     except Item.DoesNotExist:
    #         extra_context.update({'cl_header': _('Item does not exist')})
    #     else:
    #         extra_context.update({'cl_header': _(u"Serials for <{name}> in <{place}>".format(
    #             name=unicode(item.category.name),
    #             place=unicode(item.place.name)
    #         ))})
    #     return super(ItemSerialsFilteredAdmin, self).change_view(request, object_id, form_url='',
    #                                                              extra_context=extra_context)

    def get_urls(self):

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)

            return update_wrapper(wrapper, view)

        urlpatterns = [
            url(r'^(\d+)/$', wrap(self.changelist_view), name='base_item_serials_filtered_changelist'),
            # url(r'^(\d+)/(\d+)$', wrap(self.change_view), name='base_item_serials_filtered_change'),
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

    def has_add_permission(self, request):
        return False

    def get_queryset(self, request):
        qs = super(OrderItemSerialAdmin, self).get_queryset(request).select_related(
            'item', 'item__category', 'item__place'
        )
        return qs.filter(
            item__category_id__in=get_descendants_ids(ItemCategory, 89),  # FIXME
            item__place_id__in=get_descendants_ids(Place, 14)             # FIXME
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

    def has_add_permission(self, request):
        return False

    def get_queryset(self, request):
        qs = super(ContractItemSerialAdmin, self).get_queryset(request).select_related(
            'item', 'item__category', 'item__place'
        )
        return qs.filter(
            item__category_id__in=get_descendants_ids(ItemCategory, 88),  # FIXME
            item__place_id__in=get_descendants_ids(Place, 14)             # FIXME
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
        if self.place_id:
            qs = qs.filter(Q(source_id=self.place_id) | Q(destination_id=self.place_id))
        if self.category_id:
            qs = qs.filter(category_id=self.category_id)
        return qs

    def changelist_view(self, request, place_id=None, category_id=None, extra_context=None):  # pylint:disable=arguments-differ
        self.place_id = int(place_id or "0")
        self.category_id = int(category_id or "0")
        extra_context = extra_context or {}
        try:
            place = Place.objects.get(pk=place_id)
        except Place.DoesNotExist:
            place_name = "any place"
        else:
            place_name = place.name
        if category_id:
            try:
                category = ItemCategory.objects.get(pk=category_id)
            except ItemCategory.DoesNotExist:
                category_name = "any category"
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


@admin.register(FixSerialTransform)
class FixSerialTransformAdmin(admin.ModelAdmin):
    search_fields = ['old_serial', 'new_serial']
    list_display = ['timestamp', 'category', 'old_serial', 'new_serial']

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(self.readonly_fields)
        readonly_fields.extend(['category', 'timestamp'])
        if obj and obj.pk:
            readonly_fields.extend(['old_serial', 'new_serial'])
        return readonly_fields


@admin.register(FixCategoryMerge)
class FixCategoryMergeAdmin(admin.ModelAdmin):
    search_fields = ['old_category__name', 'new_category__name']
    list_display = ['timestamp', 'old_category', 'new_category']
    form = FixCategoryMergeForm

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(self.readonly_fields)
        readonly_fields.extend(['data', 'timestamp', 'old_category_sav_id', 'old_category_sav_name'])
        if obj and obj.pk:
            readonly_fields.extend(['old_category', 'new_category'])
        return readonly_fields


@admin.register(Cell)
class CellAdmin(FiltersMixin, admin.ModelAdmin):
    search_fields = ['name']
    list_display = ['name', 'place']
    list_filter = (('place', RelatedAutocompleteFilter), )
    form = CellForm


@admin.register(CellItem)
class CellItem(FiltersMixin, admin.ModelAdmin):
    search_fields = ['serial__serial']
    list_filter = (
        ('place', RelatedAutocompleteFilter),
        ('category', RelatedAutocompleteFilter),
        ('cell', RelatedAutocompleteFilter),
        'cell_isnull'
    )
    list_display = ['place', 'cell', 'category', 'serial', 'suggested_place']
    form = CellItemForm
    action_form = CellItemActionForm
    readonly_fields = ['cell_isnull']

    def update_cell(self, request, queryset):
        cell_name = request.POST['cell']
        place = queryset[0].place
        try:
            cell = Cell.objects.get(place=place, name=cell_name)
        except Cell.DoesNotExist:
            self.message_user(request, _("Selected cell does not exist"), level=messages.ERROR)
        else:
            qs = queryset.filter(place=place)
            cnt = qs.count()
            if not cnt == queryset.count():
                self.message_user(request, _("All items must be in same place"), level=messages.ERROR)
            else:
                qs.update(cell=cell)
                self.message_user(request, _("Updated items count: {cnt}, Cell: {cell}".format(
                    cnt=cnt,
                    cell=cell.name
                )), level=messages.SUCCESS)

    update_cell.short_description = _('Update cell of selected rows')

    actions = [update_cell]