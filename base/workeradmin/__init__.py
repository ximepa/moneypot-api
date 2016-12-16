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
from base.models import Place, StorageToWorkerTransaction
from .forms import WorkersAdminAuthenticationForm, ItemCategoryForm, PlaceForm, TransactionItemForm, \
    TransactionForm, ItemChunkForm, ItemSerialForm

from .inlines import TransactionItemInlineReadonly, TransactionItemInline

from base.admin.overrides import AdminReadOnly, InlineReadOnly, HiddenAdminModelMixin


PLACE_STORAGE_ID = settings.APP_FILTERS['PLACE_STORAGE_ID']


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


class PlaceAdmin(admin.ModelAdmin):
    search_fields = ['name', ]
    tree_auto_open = False
    form = PlaceForm
    list_display = ['name', 'is_shop']
    readonly_fields = ['timestamp', ]

workers_admin_site.register(Place, PlaceAdmin)


class StorageToWorkerTransactionAdmin(FiltersMixin, admin.ModelAdmin):
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

    def get_queryset(self, request):
        place = self.get_place(request)
        qs = super(StorageToWorkerTransactionAdmin, self).get_queryset(request).prefetch_related(
            'destination', 'source')
        return qs.filter(destination=place).order_by('-completed_at')

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