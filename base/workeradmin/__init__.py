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
from .forms import WorkersAdminAuthenticationForm, ItemCategoryForm, PlaceForm, PurchaseItemForm, TransactionItemForm, \
    PurchaseForm, TransactionForm, FixCategoryMergeForm, FixPlaceMergeForm, CellForm, CellItemActionForm, \
    ItemInlineForm, ItemChunkForm, ItemSerialForm, TransmutationForm, WarrantyForm, WarrantyInlineForm, \
    ReturnForm
from .inlines import ItemCategoryCommentInline, PurchaseItemInline, PurchaseItemInlineReadonly, \
    TransactionItemInlineReadonly, TransactionItemInline, TransactionCommentPlaceInline, TransmutationItemInline, \
    TransmutationItemInlineReadonly, ReturnItemInline, ReturnItemInlineReadonly
from base.admin.overrides import AdminReadOnly, InlineReadOnly, HiddenAdminModelMixin

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


class PlaceAdmin(admin.ModelAdmin):
    search_fields = ['name', ]
    tree_auto_open = False
    form = PlaceForm
    list_display = ['name', 'is_shop']
    readonly_fields = ['timestamp', ]

workers_admin_site.register(Place, PlaceAdmin)


