from django.contrib import admin
from django import forms
from django.db import models
from mptt.admin import MPTTModelAdmin
from django_mptt_admin.admin import DjangoMpttAdmin
from django.utils.translation import ugettext_lazy as _, ugettext
from django.conf.urls import patterns, include, url

from base.models import Unit, ItemCategory, Place, PurchaseItem, Payer, Purchase, Item, ItemSerial, ItemChunk, \
    TransactionItem, Transaction

import autocomplete_light

@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    pass


@admin.register(ItemCategory)
class ItemCategoryAdmin(DjangoMpttAdmin):
    search_fields = ['name',]
    tree_auto_open = False


@admin.register(Place)
class PlaceAdmin(DjangoMpttAdmin):
    search_fields = ['name',]
    tree_auto_open = False


@admin.register(PurchaseItem)
class PurchaseItemAdmin(admin.ModelAdmin):
    pass


@admin.register(Payer)
class PayerAdmin(admin.ModelAdmin):
    search_fields = ['name',]


class PurchaseItemForm(autocomplete_light.ModelForm):
    class Meta:
        model = PurchaseItem
        exclude = ['_chunks']


class PurchaseItemInline(admin.TabularInline):
    model = PurchaseItem
    form = PurchaseItemForm
    extra = 10
    formfield_overrides = {
        models.TextField: {'widget': forms.Textarea(
            attrs={'rows': 1, 'cols': 60}
        )},
    }


class PurchaseForm(autocomplete_light.ModelForm):
    class Meta:
        model = Purchase
        exclude = ['is_completed', 'is_prepared']


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    force_complete = forms.BooleanField(required=False, label=_("force complete"))
    form = PurchaseForm
    inlines = [PurchaseItemInline,]
    list_display = ['__unicode__', 'created_at', 'completed_at', 'source', 'destination', 'is_completed', 'is_prepared',]
    list_filter = ['source', 'destination', 'is_completed', 'is_prepared',]
    search_fields = ['source__name', 'destination__name', 'purchase_items__category__name']


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    search_fields = ['category__name', 'place__name']
    list_filter = ['category',]
    list_display = ['__unicode__', 'quantity', 'place']


@admin.register(ItemSerial)
class ItemSerialAdmin(admin.ModelAdmin):
    search_fields = ['item__category__name']
    list_filter = ['item__category',]


@admin.register(ItemChunk)
class ItemChunkAdmin(admin.ModelAdmin):
    search_fields = ['item__category__name']
    list_filter = ['item__category',]


class TransactionItemForm(autocomplete_light.ModelForm):
    class Meta:
        model = TransactionItem
        exclude = ['_chunks', 'purchase']
        autocomplete_fields = ('category',)

    def save(self, *args, **kwargs):
        ti = super(TransactionItemForm, self).save(*args, **kwargs)
        if ti.transaction.is_completed:
            print
            print "TRANSACTION RESET"
            ti.transaction.reset()


@admin.register(TransactionItem)
class TransactionItemAdmin(admin.ModelAdmin):
    pass


class TransactionForm(autocomplete_light.ModelForm):
    force_complete = forms.BooleanField(required=False, label=_("force complete"))

    class Meta:
        model = Transaction
        exclude = ['is_completed', 'is_prepared', 'is_negotiated_source',
                   'is_negotiated_destination', 'is_confirmed_source', 'is_confirmed_destination']
        autocomplete_fields = ('source', 'destination', 'items')

    def save(self, *args, **kwargs):
        t = super(TransactionForm, self).save(*args, **kwargs)
        if self.cleaned_data['force_complete']:
            t.force_complete()
        return t


class TransactionItemInline(admin.TabularInline):
    model = TransactionItem
    form = TransactionItemForm
    extra = 10
    formfield_overrides = {
        models.TextField: {'widget': forms.Textarea(
            attrs={'rows': 1, 'cols': 60}
        )},
    }


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
        TransactionItemInline
    ]


@admin.site.register_view('itemss')
class PlaceItemAdmin(admin.ModelAdmin):
    def get_urls(self):
        urls = super(PlaceItemAdmin, self).get_urls()
        info = self.model._meta.app_label, self.model._meta.module_name
        select_list_url = patterns('',
            url(r'^selectlist/$', self.selectlist_view,
                name='%s_%s_select' % info)
        )
        return select_list_url + urls

    def selectlist_view(self, request, extra_context=None):
        temp_list_display_links = self.list_display_links
        self.list_display_links = (None, )
        response = self.changelist_view(request, extra_context)
        self.list_display_links = temp_list_display_links
        return response