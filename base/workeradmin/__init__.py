# -*- encoding: utf-8 -*-
from __future__ import print_function, division, unicode_literals, absolute_import

from daterange_filter.filter import DateRangeFilter
from django.conf import settings
from django.contrib import admin
from django.contrib import messages
from django.contrib.admin.utils import quote
from django.core.exceptions import ValidationError, PermissionDenied
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.utils.html import mark_safe
from django.utils.translation import ugettext_lazy as _, ugettext
from django_mptt_admin import util
from django_mptt_admin.admin import DjangoMpttAdmin
from filebrowser.settings import ADMIN_THUMBNAIL
from grappelli_filters import RelatedAutocompleteFilter, FiltersMixin

from base.admin import MPTTRelatedAutocompleteFilter
from base.models import Place, StorageToWorkerTransaction, WorkersItem, WorkersReturn, WorkersUsed, WorkersInstalled
from .forms import WorkersAdminAuthenticationForm, ItemCategoryForm, PlaceForm, TransactionItemForm, \
    TransactionForm, ItemChunkForm, ItemSerialForm, ReturnForm, TransactionDestinationForm

from .inlines import TransactionItemInlineReadonly, TransactionItemInline, ReturnItemInline, ReturnItemInlineReadonly, \
    TransactionItemDestinationInline

from base.admin.overrides import AdminReadOnly, InlineReadOnly, HiddenAdminModelMixin


PLACE_STORAGE_ID = settings.APP_FILTERS['PLACE_STORAGE_ID']
PLACE_USED_ID = settings.APP_FILTERS['PLACE_USED_ID']
PLACE_ADDRESS_ID = settings.APP_FILTERS['PLACE_ADDRESS_ID']



try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode

from django.contrib.admin import AdminSite


class WorkersAdminSite(AdminSite):
    site_header = 'Склад'
    login_form = WorkersAdminAuthenticationForm

    def has_permission(self, request):
        """
        Returns True if the given HttpRequest has permission to view
        *at least one* page in the admin site.
        """
        return request.user.is_active


workers_admin_site = WorkersAdminSite(name='workers_admin')
workers_admin_site.disable_action('delete_selected')


class GetPlaceMixin(object):

    @staticmethod
    def get_place(request):
        place = None
        try:
            place = request.user.profile.place
        except Exception as e:
            print(e)
        if not place:
            raise PermissionDenied(_("user does not have configured place in profile"))
        return place

    def get_places_ids(self, request):
        return self.get_place(request).get_descendants(include_self=True).values_list('id', flat=True)


class PlaceAdmin(admin.ModelAdmin):
    search_fields = ['name', ]
    tree_auto_open = False
    form = PlaceForm
    list_display = ['name', 'is_shop']
    readonly_fields = ['timestamp', ]

workers_admin_site.register(Place, PlaceAdmin)


class StorageToWorkerTransactionAdmin(FiltersMixin, GetPlaceMixin, admin.ModelAdmin):
    class Media:
        js = ('base/js/transaction_source_item_autocomplete.js',)

    form = TransactionForm
    list_display = [
        '__str__', 'created_at', 'completed_at', 'is_completed',
    ]
    list_filter = [
        'is_completed',
        ('source', MPTTRelatedAutocompleteFilter),
    ]
    search_fields = ['transaction_items__category__name',]
    inlines = [
        TransactionItemInline
    ]

    def get_queryset(self, request):
        places = self.get_places_ids(request)
        qs = super(StorageToWorkerTransactionAdmin, self).get_queryset(request).prefetch_related(
            'destination', 'source')
        return qs.filter(destination_id__in=places).order_by('-completed_at')

    def has_delete_permission(self, request, obj=None):
        if obj and obj.is_completed:
            return False
        else:
            return super(StorageToWorkerTransactionAdmin, self).has_delete_permission(request, obj)

    def get_inline_instances(self, request, obj=None):
        inline_instances = []

        if obj and obj.is_completed:
            _inlines = [TransactionItemInlineReadonly, ]
        else:
            _inlines = self.inlines

        for inline_class in _inlines:
            inline = inline_class(self.model, self.admin_site)
            inline_instances.append(inline)
        return inline_instances

    def save_model(self, request, obj, form, change):
        if not obj.source_id:
            obj.source_id = PLACE_STORAGE_ID
        if not obj.destination_id:
            obj.destination_id = self.get_place(request).id
        obj.save()


workers_admin_site.register(StorageToWorkerTransaction, StorageToWorkerTransactionAdmin)


class WorkersItemAdmin(FiltersMixin, GetPlaceMixin, AdminReadOnly):

    search_fields = ['category__name', 'place__name']
    list_filter = [
        ('category', MPTTRelatedAutocompleteFilter),
        ('place', MPTTRelatedAutocompleteFilter),
    ]
    list_display = ['category_name', 'quantity', 'place']
    change_list_template = 'admin/proxy_change_list.html'
    change_form_template = 'admin/proxy_change_form.html'

    def get_queryset(self, request):
        places = self.get_places_ids(request)
        qs = super(WorkersItemAdmin, self).get_queryset(request).prefetch_related('serials', 'category', 'place')
        return qs.filter(place_id__in=places).order_by('-category__name')

    def changelist_view(self, request, extra_context=None):  # pylint:disable=arguments-differ
        extra_context = extra_context or {}
        extra_context.update({'cl_header': "Залишки: %s" % self.get_place(request)})
        extra_context.update({'export_place_id': self.get_place(request).id})
        extra_context.update({'hide_zero_switch': True})
        view = super(WorkersItemAdmin, self).changelist_view(request, extra_context=extra_context)
        return view

workers_admin_site.register(WorkersItem, WorkersItemAdmin)


class WorkersReturnAdmin(FiltersMixin, GetPlaceMixin, admin.ModelAdmin):
    class Media:
        js = ('base/js/transmutation_source_item_autocomplete.js',)

    form = ReturnForm
    list_display = [
        '__str__', 'created_at', 'is_completed', 'completed_at', 'source', 'destination',
    ]
    list_filter = [
        ('source', MPTTRelatedAutocompleteFilter),
        'is_completed',
    ]
    search_fields = ['source__name', 'transaction_items__category__name']
    inlines = [
        ReturnItemInline
    ]

    def get_queryset(self, request):
        place = self.get_place(request)
        qs = super(WorkersReturnAdmin, self).get_queryset(request).prefetch_related('source', 'destination')
        return qs.filter(source=place).order_by('-created_at')

    def has_delete_permission(self, request, obj=None):
        if obj and obj.is_completed:
            return False
        else:
            return super(WorkersReturnAdmin, self).has_delete_permission(request, obj)

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(self.readonly_fields)
        if obj and obj.is_completed:
            readonly_fields.extend(['source', 'destination', 'completed_at'])
        return readonly_fields

    def get_fields(self, request, obj=None):
        fields = super(WorkersReturnAdmin, self).get_fields(request, obj)
        if obj and obj.is_completed:
            fields.remove('force_complete')
        return fields

    def get_inline_instances(self, request, obj=None):
        inline_instances = []
        if obj and obj.transaction_ptr.is_completed:
            _inlines = [ReturnItemInlineReadonly, ]
        else:
            _inlines = self.inlines
        self._obj = obj

        for inline_class in _inlines:
            inline = inline_class(self.model, self.admin_site)
            inline_instances.append(inline)
        return inline_instances

    def save_model(self, request, obj, form, change):
        if not obj.source_id:
            obj.source_id = self.get_place(request).id
        if not obj.destination_id:
            obj.destination_id = PLACE_STORAGE_ID
        obj.save()

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            instance.save()
        formset.save_m2m()
        if self._obj:
            t = self._obj
            if hasattr(t, "is_pending") and t.is_pending:
                # print "complete pending transaction"
                t.is_pending = False
                t.ret()

workers_admin_site.register(WorkersReturn, WorkersReturnAdmin)


class WorkersUsedAdmin(FiltersMixin, GetPlaceMixin, admin.ModelAdmin):
    class Media:
        js = ('base/js/transaction_source_item_autocomplete.js',)

    form = TransactionForm
    list_display = [
        '__str__', 'created_at', 'completed_at', 'is_completed',
    ]
    list_filter = [
        'is_completed',
        ('source', MPTTRelatedAutocompleteFilter),
    ]
    search_fields = ['transaction_items__category__name',]
    inlines = [
        TransactionItemInline
    ]

    def get_queryset(self, request):
        places = self.get_places_ids(request)
        qs = super(WorkersUsedAdmin, self).get_queryset(request).prefetch_related(
            'destination', 'source')
        return qs.filter(source_id__in=places, destination_id=PLACE_USED_ID).order_by('-completed_at')

    def has_delete_permission(self, request, obj=None):
        if obj and obj.is_completed:
            return False
        else:
            return super(WorkersUsedAdmin, self).has_delete_permission(request, obj)

    def get_inline_instances(self, request, obj=None):
        inline_instances = []

        if obj and obj.is_completed:
            _inlines = [TransactionItemInlineReadonly, ]
        else:
            _inlines = self.inlines

        for inline_class in _inlines:
            inline = inline_class(self.model, self.admin_site)
            inline_instances.append(inline)
        return inline_instances

    def save_model(self, request, obj, form, change):
        if not obj.source_id:
            obj.source_id = self.get_place(request).id
        if not obj.destination_id:
            obj.destination_id = PLACE_USED_ID
        obj.save()


workers_admin_site.register(WorkersUsed, WorkersUsedAdmin)


class WorkersInstalledAdmin(FiltersMixin, GetPlaceMixin, admin.ModelAdmin):
    class Media:
        js = ('base/js/transaction_source_item_autocomplete.js',)

    form = TransactionForm
    list_display = [
        '__str__', 'created_at', 'completed_at', 'is_completed',
    ]
    list_filter = [
        'is_completed',
        ('source', MPTTRelatedAutocompleteFilter),
    ]
    search_fields = ['transaction_items__category__name',]
    inlines = [
        TransactionItemDestinationInline
    ]

    def get_queryset(self, request):
        places = self.get_places_ids(request)
        qs = super(WorkersInstalledAdmin, self).get_queryset(request).prefetch_related(
            'destination', 'source')
        return qs.filter(Q(source_id__in=places) & ~Q(destination_id=PLACE_USED_ID)).order_by('-completed_at')

    def has_delete_permission(self, request, obj=None):
        if obj and obj.is_completed:
            return False
        else:
            return super(WorkersInstalledAdmin, self).has_delete_permission(request, obj)

    def get_inline_instances(self, request, obj=None):
        inline_instances = []

        if obj and obj.is_completed:
            _inlines = [TransactionItemInlineReadonly, ]
        else:
            _inlines = self.inlines

        for inline_class in _inlines:
            inline = inline_class(self.model, self.admin_site)
            inline_instances.append(inline)
        return inline_instances

    def save_model(self, request, obj, form, change):
        if not obj.source_id:
            obj.source_id = self.get_place(request).id
        if not obj.destination_id:
            obj.destination_id = PLACE_ADDRESS_ID
        obj.save()


workers_admin_site.register(WorkersInstalled, WorkersInstalledAdmin)

