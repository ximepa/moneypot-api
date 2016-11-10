# -*- encoding: utf-8 -*-
from __future__ import print_function, division, unicode_literals, absolute_import

from daterange_filter.filter import DateRangeFilter
from django.conf import settings
from django.contrib import admin
from django.contrib import messages
from django.contrib.admin.utils import quote
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.utils.html import mark_safe
from django.utils.translation import ugettext_lazy as _, ugettext
from django_mptt_admin import util
from django_mptt_admin.admin import DjangoMpttAdmin
from filebrowser.settings import ADMIN_THUMBNAIL
from grappelli_filters import RelatedAutocompleteFilter, FiltersMixin

from base.models import Unit, ItemCategory, Place, PurchaseItem, Payer, Purchase, Item, ItemSerial, ItemChunk, \
    TransactionItem, Transaction, Cell, GeoName, Warranty
from .actions import process_to_void, update_cell
from .filters import MPTTRelatedAutocompleteFilter
from .forms import ItemCategoryForm, PlaceForm, PurchaseItemForm, TransactionItemForm, PurchaseForm, TransactionForm, \
    FixCategoryMergeForm, FixPlaceMergeForm, CellForm, CellItemActionForm, ItemInlineForm, ItemChunkForm, \
    ItemSerialForm, TransmutationForm, WarrantyForm, WarrantyInlineForm, ReturnForm
from .functions import create_model_admin
from .inlines import ItemCategoryCommentInline, PurchaseItemInline, PurchaseItemInlineReadonly, \
    TransactionItemInlineReadonly, TransactionItemInline, TransactionCommentPlaceInline, TransmutationItemInline, \
    TransmutationItemInlineReadonly, ReturnItemInline, ReturnItemInlineReadonly
from .overrides import AdminReadOnly, InlineReadOnly, HiddenAdminModelMixin

try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode

from django.contrib.admin import AdminSite


class MyAdminSite(AdminSite):
    site_header = 'Super Admin'


admin_site = MyAdminSite(name='myadmin')


class GeoNameAdmin(admin.ModelAdmin):
    search_fields = ['name']
    readonly_fields = ['timestamp', ]
    list_display = ['name', 'timestamp']
    list_filter = [('timestamp', DateRangeFilter), ]


admin_site.register(GeoName, GeoNameAdmin)


class UnitAdmin(admin.ModelAdmin):
    search_fields = ['name']


admin_site.register(Unit, UnitAdmin)


class ItemCategoryAdmin(DjangoMpttAdmin):
    class Media:
        js = ('base/js/category_parent_autocomplete.js',)

    change_tree_template = u'admin/mptt_change_list.html'
    form = ItemCategoryForm
    search_fields = ['name', ]
    tree_auto_open = False
    inlines = [ItemCategoryCommentInline]
    list_display = ['name', 'image_thumbnail', 'timestamp']
    list_filter = [('timestamp', DateRangeFilter), ]
    readonly_fields = ['timestamp', ]

    def image_thumbnail(self, obj):
        if obj.photo:
            if obj.photo.filetype == "Image":
                return '<a href="%s"><img src="%s" /></a>' % (
                    obj.photo.url, obj.photo.version_generate(ADMIN_THUMBNAIL).url)
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
                storage_url=reverse(
                    'admin:base_place_item_changelist',
                    args=(settings.APP_FILTERS["PLACE_STORAGE_ID"],)
                ) + "?category__id__in=%s" % pk,
                move_url=self.get_admin_url('move', (quote(pk),))
            )

        return util.get_tree_from_queryset(qs, handle_create_node, max_level)


admin_site.register(ItemCategory, ItemCategoryAdmin)


class PlaceAdmin(DjangoMpttAdmin):
    change_tree_template = u'admin/mptt_change_list.html'
    search_fields = ['name', ]
    tree_auto_open = False
    form = PlaceForm
    list_display = ['name', 'is_shop', 'items_changelist_link', 'timestamp']
    list_filter = [('timestamp', DateRangeFilter), ]
    readonly_fields = ['timestamp', ]

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


admin_site.register(Place, PlaceAdmin)


class PurchaseItemAdmin(admin.ModelAdmin):
    pass


admin_site.register(PurchaseItem, PurchaseItemAdmin)


class PayerAdmin(admin.ModelAdmin):
    search_fields = ['name', ]


admin_site.register(Payer, PayerAdmin)


class PurchaseAdmin(FiltersMixin, admin.ModelAdmin):
    class Media:
        js = ('base/js/purchase_source_item_autocomplete.js',)

    form = PurchaseForm
    inlines = [PurchaseItemInline, ]
    list_display = ['__str__', 'created_at', 'completed_at', 'source', 'destination', 'is_completed',
                    'is_prepared', ]
    list_filter = [
        ('source', MPTTRelatedAutocompleteFilter),
        ('destination', MPTTRelatedAutocompleteFilter),
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
        # if obj and obj.is_completed:
        #     readonly_fields.extend(['source', 'destination', 'completed_at', 'is_auto_source'])
        #     dir(self.form)
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

        self._obj = obj

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
                completed_instance = PurchaseItem.objects.get(pk=instance.pk)
                if not completed_instance.pk == instance.pk or \
                        not completed_instance.quantity == instance.quantity or \
                        not completed_instance.category == instance.category or \
                        not completed_instance.serials == instance.serials:
                    raise ValidationError(ugettext("purchase items data is read only!"))
            instance.save()
        formset.save_m2m()
        if self._obj:
            p = self._obj
            if hasattr(p, "is_pending") and p.is_pending:
                # print "complete pending purchase"
                p.is_pending = False
                p.complete()


admin_site.register(Purchase, PurchaseAdmin)


class TransactionItemAdmin(HiddenAdminModelMixin, admin.ModelAdmin):
    pass


admin_site.register(TransactionItem, TransactionItemAdmin)


class TransactionAdmin(FiltersMixin, admin.ModelAdmin):
    class Media:
        js = ('base/js/transaction_source_item_autocomplete.js',)

    form = TransactionForm
    list_display = [
        '__str__', 'created_at', 'completed_at',
        'source', 'destination', 'is_completed', 'is_prepared',
        # 'is_negotiated_source', 'is_negotiated_destination', 'is_confirmed_source',
        # 'is_confirmed_destination'
    ]
    list_filter = [
        ('source', MPTTRelatedAutocompleteFilter),
        ('destination', MPTTRelatedAutocompleteFilter),
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

    # def get_readonly_fields(self, request, obj=None):
    #     readonly_fields = list(self.readonly_fields)
    #     # if obj and obj.is_completed:
    #     #     readonly_fields.extend(['source', 'destination', 'completed_at'])
    #     return readonly_fields

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

        self._obj = obj

        for inline_class in inlines:
            inline = inline_class(self.model, self.admin_site)
            inline_instances.append(inline)
        return inline_instances

    def save_formset(self, request, form, formset, change):
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
        if self._obj:
            t = self._obj
            if hasattr(t, "is_pending") and t.is_pending:
                # print "complete pending transaction"
                t.is_pending = False
                t.complete()

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


admin_site.register(Transaction, TransactionAdmin)


class ItemAdmin(FiltersMixin, admin.ModelAdmin):
    search_fields = ['category__name', 'place__name']
    list_filter = [('category', MPTTRelatedAutocompleteFilter), 'cell']
    list_display = ['category_name', 'quantity', 'place', 'cell']


admin_site.register(Item, ItemAdmin)


class ItemSerialAdmin(FiltersMixin):
    class Media:
        # js = ('base/js/place_item_changelist_autocomplete.js',)
        js = ('base/js/serial_purchase_autocomplete.js',)

    form = ItemSerialForm

    # def get_readonly_fields(self, request, obj=None):
    #     if obj and obj.pk:
    #         result = list(set(
    #                 [field.name for field in self.opts.local_fields] +
    #                 [field.name for field in self.opts.local_many_to_many]
    #         ))
    #         if 'id' in result:
    #             result.remove('id')
    #         return result
    #     return super(ItemSerialAdmin, self).get_readonly_fields(request, obj)

    def get_queryset(self, request):
        return super(ItemSerialAdmin, self).get_queryset(request).select_related('item', 'item__category',
                                                                                 'item__place')

    def owner(self, instance):
        return instance.item.place.name

    def serial_movement_changelist_link(self, obj):
        link = reverse("admin:base_serial_movement_filtered_changelist", args=[obj.id])
        return mark_safe(u'<a href="%s">%s</a>' % (link, _("movement history")))

    def get_list_display(self, request):
        list_display = self.list_display[:]
        if request.user.has_perm('base.view_item_price'):
            list_display.append('price')
        return list_display

    search_fields = ['item__category__name', 'serial']
    list_filter = [
        ('item__category', MPTTRelatedAutocompleteFilter),
        ('item__place', MPTTRelatedAutocompleteFilter),
        'cell'
    ]
    list_display = ['serial', 'category_name', 'owner', 'cell', 'serial_movement_changelist_link']


admin_site.register(ItemSerial, ItemSerialAdmin)


class ItemChunkAdmin(FiltersMixin, admin.ModelAdmin):
    search_fields = ['item__category__name']
    list_filter = [
        ('item__category', MPTTRelatedAutocompleteFilter),
        ('item__place', MPTTRelatedAutocompleteFilter),
    ]
    list_display = ['__str__', 'category_name', 'place_name', 'cell']
    form = ItemChunkForm
    actions = [update_cell]
    action_form = CellItemActionForm

    # def get_readonly_fields(self, request, obj=None):
    #     fields = super(ItemChunkAdmin, self).get_readonly_fields(request, obj)
    #     fields.remove('cell')
    #     return fields


admin_site.register(ItemChunk, ItemChunkAdmin)


class CellAdmin(FiltersMixin, admin.ModelAdmin):
    search_fields = ['name']
    list_display = ['name', 'place']
    list_filter = (('place', RelatedAutocompleteFilter),)
    form = CellForm


admin_site.register(Cell, CellAdmin)


class WarrantyAdmin(FiltersMixin, admin.ModelAdmin):
    search_fields = ['serial__serial', 'serial__item__category__name']
    list_display = ['__str__', 'category_name', 'date']
    list_filter = [
        ('serial__item__category', MPTTRelatedAutocompleteFilter)
    ]
    form = WarrantyForm


admin_site.register(Warranty, WarrantyAdmin)
